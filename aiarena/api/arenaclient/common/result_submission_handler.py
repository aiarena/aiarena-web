import logging
from dataclasses import dataclass
from typing import Any

from django.conf import settings
from django.db import transaction
from django.db.models import F, Prefetch, Sum

from constance import config
from rest_framework.exceptions import APIException

from aiarena.core.models import (
    BotCrashLimitAlert,
    CompetitionParticipation,
    Match,
    MatchParticipation,
    MatchTag,
    Result,
    Tag,
)
from aiarena.core.services import Bots, BotStatistics
from aiarena.core.services.internal.rounds import update_round_if_completed
from aiarena.core.utils import parse_tags

from .serializers import (
    SubmitResultBotSerializer,
    SubmitResultParticipationSerializer,
    SubmitResultResultSerializer,
)


logger = logging.getLogger(__name__)


def handle_result_submission(match_id, result_data):
    with transaction.atomic():
        match = Match.objects.prefetch_related(
            Prefetch("matchparticipation_set", MatchParticipation.objects.all().select_related("bot"))
        ).get(id=match_id)
        # validate result
        result = SubmitResultResultSerializer(
            data={
                "match": match_id,
                "type": result_data["type"],
                "replay_file": result_data.get("replay_file"),
                "game_steps": result_data["game_steps"],
                "submitted_by": result_data["submitted_by"].pk,
                "arenaclient_log": result_data.get("arenaclient_log"),
            }
        )
        result.is_valid(raise_exception=True)
        # validate participants
        p1_instance = match.matchparticipation_set.get(participant_number=1)
        result_cause = Result.calculate_result_cause(result_data["type"])
        participant1 = SubmitResultParticipationSerializer(
            instance=p1_instance,
            data={
                "avg_step_time": result_data.get("bot1_avg_step_time"),
                "match_log": result_data.get("bot1_log"),
                "result": p1_instance.calculate_relative_result(result_data["type"]),
                "result_cause": result_cause,
            },
            partial=True,
        )
        participant1.is_valid(raise_exception=True)
        p2_instance = match.matchparticipation_set.get(participant_number=2)
        participant2 = SubmitResultParticipationSerializer(
            instance=p2_instance,
            data={
                "avg_step_time": result_data.get("bot2_avg_step_time"),
                "match_log": result_data.get("bot2_log"),
                "result": p2_instance.calculate_relative_result(result_data["type"]),
                "result_cause": result_cause,
            },
            partial=True,
        )
        participant2.is_valid(raise_exception=True)

        result_submission = ResultSubmission(
            match=match,
            p1_instance=p1_instance,
            p2_instance=p2_instance,
            participant1=participant1,
            participant2=participant2,
            result=result,
            bot1_data=result_data.get("bot1_data"),
            bot2_data=result_data.get("bot2_data"),
            bot1_tags=result_data.get("bot1_tags"),
            bot2_tags=result_data.get("bot2_tags"),
        )

        return submit_result(result_submission)


@dataclass
class ResultSubmission:
    """
    Data Transfer Object for result submission.
    """

    match: Match
    p1_instance: MatchParticipation
    p2_instance: MatchParticipation
    participant1: SubmitResultParticipationSerializer
    participant2: SubmitResultParticipationSerializer
    result: SubmitResultResultSerializer
    bot1_data: Any | None
    bot2_data: Any | None
    bot1_tags: list | None
    bot2_tags: list | None


@dataclass
class ResultSubmissionConfig:
    enable_elo_sanity_check: bool = config.ENABLE_ELO_SANITY_CHECK
    bot_consecutive_crash_limit: int = config.BOT_CONSECUTIVE_CRASH_LIMIT


def submit_result(
    result_submission: ResultSubmission, config: ResultSubmissionConfig = ResultSubmissionConfig()
) -> Result:
    """
    Processes the result of a match.
    """
    # validate bots
    if not result_submission.p1_instance.bot.is_in_match(result_submission.match.id):
        logger.warning(
            f"A result was submitted for match {result_submission.match.id}, "
            f"which Bot {result_submission.p1_instance.bot.name} isn't currently in!"
        )
        raise APIException(
            f"Unable to log result: Bot {result_submission.p1_instance.bot.name} is not currently in this match!"
        )
    if not result_submission.p2_instance.bot.is_in_match(result_submission.match.id):
        logger.warning(
            f"A result was submitted for match {result_submission.match.id}, "
            f"which Bot {result_submission.p2_instance.bot.name} isn't currently in!"
        )
        raise APIException(
            f"Unable to log result: Bot {result_submission.p2_instance.bot.name} is not currently in this match!"
        )
    bot1 = None
    bot2 = None
    match_is_requested = result_submission.match.is_requested
    # should we update the bot data?
    if (
        result_submission.p1_instance.use_bot_data
        and result_submission.p1_instance.update_bot_data
        and not match_is_requested
    ):
        if result_submission.bot1_data is not None and not match_is_requested:
            bot1_dict = {"bot_data": result_submission.bot1_data}
            bot1 = SubmitResultBotSerializer(instance=result_submission.p1_instance.bot, data=bot1_dict, partial=True)
            bot1.is_valid(raise_exception=True)
    if (
        result_submission.p2_instance.use_bot_data
        and result_submission.p2_instance.update_bot_data
        and not match_is_requested
    ):
        if result_submission.bot2_data is not None and not match_is_requested:
            bot2_dict = {"bot_data": result_submission.bot2_data}
            bot2 = SubmitResultBotSerializer(instance=result_submission.p2_instance.bot, data=bot2_dict, partial=True)
            bot2.is_valid(raise_exception=True)
    # save models
    result = result_submission.result.save()
    participant1 = result_submission.participant1.save()
    participant2 = result_submission.participant2.save()
    # save these after the others so if there's a validation error,
    # then the bot data files don't need reverting to match their hashes.
    # This could probably be done more fool-proof by actually rolling back the files on a transaction fail.
    if bot1 is not None:
        bot1.save()
    if bot2 is not None:
        bot2.save()
    # Save Tags
    bot1_user = participant1.bot.user
    bot2_user = participant2.bot.user
    parsed_bot1_tags = parse_tags(result_submission.bot1_tags)
    parsed_bot2_tags = parse_tags(result_submission.bot2_tags)
    # Union tags if both bots belong to the same user
    if bot1_user == bot2_user:
        total_tags = list(
            set(parsed_bot1_tags if parsed_bot1_tags else []) | set(parsed_bot2_tags if parsed_bot2_tags else [])
        )

        if total_tags:
            total_match_tags = []
            for tag in total_tags:
                tag_obj = Tag.objects.get_or_create(name=tag)
                total_match_tags.append(MatchTag.objects.get_or_create(tag=tag_obj[0], user=bot1_user)[0])
            # remove tags for this match that belong to this user and were not sent in the form
            result_submission.match.tags.remove(
                *result_submission.match.tags.filter(user=bot1_user).exclude(id__in=[mt.id for mt in total_match_tags])
            )
            # add everything, this shouldn't cause duplicates
            result_submission.match.tags.add(*total_match_tags)
    else:
        if parsed_bot1_tags:
            p1_match_tags = []
            for tag in parsed_bot1_tags:
                tag_obj = Tag.objects.get_or_create(name=tag)
                p1_match_tags.append(MatchTag.objects.get_or_create(tag=tag_obj[0], user=bot1_user)[0])
            # remove tags for this match that belong to this user and were not sent in the form
            result_submission.match.tags.remove(
                *result_submission.match.tags.filter(user=bot1_user).exclude(id__in=[mt.id for mt in p1_match_tags])
            )
            # add everything, this shouldn't cause duplicates
            result_submission.match.tags.add(*p1_match_tags)

        if parsed_bot2_tags:
            p2_match_tags = []
            for tag in parsed_bot2_tags:
                tag_obj = Tag.objects.get_or_create(name=tag)
                p2_match_tags.append(MatchTag.objects.get_or_create(tag=tag_obj[0], user=bot2_user)[0])
            # remove tags for this match that belong to this user and were not sent in the form
            result_submission.match.tags.remove(
                *result_submission.match.tags.filter(user=bot2_user).exclude(id__in=[mt.id for mt in p2_match_tags])
            )
            # add everything, this shouldn't cause duplicates
            result_submission.match.tags.add(*p2_match_tags)
    result_submission.match.result = result
    result_submission.match.save()
    # Only do these actions if the match is part of a round
    if result.match.round is not None:
        update_round_if_completed(result.match.round)

        # Update and record ELO figures
        participant1.starting_elo, participant2.starting_elo = result.get_initial_elos
        result.adjust_elo()

        initial_elo_sum = participant1.starting_elo + participant2.starting_elo

        # Calculate the change in ELO
        # the bot elos have changed so refresh them
        # todo: instead of having to refresh, return data from adjust_elo and apply it here
        sp1, sp2 = result.get_competition_participants
        participant1.resultant_elo = sp1.elo
        participant2.resultant_elo = sp2.elo
        participant1.elo_change = participant1.resultant_elo - participant1.starting_elo
        participant2.elo_change = participant2.resultant_elo - participant2.starting_elo
        participant1.save()
        participant2.save()

        resultant_elo_sum = participant1.resultant_elo + participant2.resultant_elo
        if initial_elo_sum != resultant_elo_sum:
            logger.critical(
                f"Initial and resultant ELO sum mismatch: "
                f"Result {result.id}. "
                f"initial_elo_sum: {initial_elo_sum}. "
                f"resultant_elo_sum: {resultant_elo_sum}. "
                f"participant1.elo_change: {participant1.elo_change}. "
                f"participant2.elo_change: {participant2.elo_change}"
            )

        if config.enable_elo_sanity_check:
            logger.debug("ENABLE_ELO_SANITY_CHECK enabled. Performing check.")

            # test here to check ELO total and ensure no corruption
            match_competition = result.match.round.competition
            expected_elo_sum = (
                settings.ELO_START_VALUE
                * CompetitionParticipation.objects.filter(competition=match_competition).count()
            )
            actual_elo_sum = CompetitionParticipation.objects.filter(competition=match_competition).aggregate(
                Sum("elo")
            )

            if actual_elo_sum["elo__sum"] != expected_elo_sum:
                logger.critical(
                    f"ELO SANITY CHECK FAILURE: ELO sum of {actual_elo_sum['elo__sum']} did not match expected value "
                    f"of {expected_elo_sum} upon submission of result {result.id}"
                )
            else:
                logger.debug("ENABLE_ELO_SANITY_CHECK passed!")

        else:
            logger.debug("ENABLE_ELO_SANITY_CHECK disabled. Skipping check.")

        BotStatistics(sp1).update_stats_based_on_result(result, sp2)
        BotStatistics(sp2).update_stats_based_on_result(result, sp1)

        if result.is_crash_or_timeout:
            try:
                run_consecutive_crashes_check(
                    result.get_causing_participant_of_crash_or_timeout_result, config.bot_consecutive_crash_limit
                )
            except Exception as e:
                logger.exception(e)
    return result


def run_consecutive_crashes_check(triggering_participation: MatchParticipation, consecutive_crash_limit: int):
    """
    Checks to see whether the last X results for a participant are crashes and, if so, sends an alert.
    :param triggering_participation: The participant who triggered this check and whose bot we should run the check for.
    :param consecutive_crash_limit: The number of consecutive crashes to check for.
    :return:
    """

    if consecutive_crash_limit < 1:
        return  # Check is disabled

    if not triggering_participation.bot.competition_participations.filter(active=True).exists():
        return  # No use running the check - bot is already inactive.

    # Get recent match participation records for this bot since its last update
    recent_participations = MatchParticipation.objects.filter(
        bot=triggering_participation.bot, match__result__isnull=False, match__started__gt=F("bot__bot_zip_updated")
    ).order_by("-match__result__created")[:consecutive_crash_limit]

    # if there's not enough participations yet, then exit without action
    if recent_participations.count() < consecutive_crash_limit:
        return

    # if any of the previous results weren't a crash or already triggered a crash limit alert, then exit without action
    for recent_participation in recent_participations:
        if not recent_participation.crashed:
            return
        elif recent_participation.triggered_a_crash_limit_alert:
            return

    # Log a crash alert
    BotCrashLimitAlert.objects.create(triggering_match_participation=triggering_participation)

    # If we get to here, all the results were crashes, so take action
    Bots.send_crash_alert(triggering_participation.bot)
