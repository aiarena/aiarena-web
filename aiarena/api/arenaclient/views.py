import logging
from wsgiref.util import FileWrapper

from django.conf import settings
from django.core.cache import cache
from django.db import transaction
from django.db.models import Prefetch, Sum
from django.http import HttpResponse

from constance import config
from rest_framework import mixins, serializers, status, viewsets
from rest_framework.decorators import action
from rest_framework.exceptions import APIException, PermissionDenied
from rest_framework.fields import FileField, FloatField
from rest_framework.response import Response
from rest_framework.reverse import reverse

from aiarena.api.arenaclient.ac_coordinator import ACCoordinator
from aiarena.api.arenaclient.exceptions import LadderDisabled, NoGameForClient
from aiarena.api.arenaclient.s3_helpers import get_file_s3_url_with_content_disposition, is_s3_file
from aiarena.core.api import BotStatistics
from aiarena.core.models import (
    Bot,
    BotCrashLimitAlert,
    CompetitionParticipation,
    Map,
    Match,
    MatchParticipation,
    MatchTag,
    Result,
    Tag,
)
from aiarena.core.models.arena_client_status import ArenaClientStatus
from aiarena.core.permissions import IsArenaClient, IsArenaClientOrAdminUser
from aiarena.core.utils import parse_tags
from aiarena.core.validators import validate_not_inf, validate_not_nan


logger = logging.getLogger(__name__)


class MapSerializer(serializers.ModelSerializer):
    class Meta:
        model = Map
        fields = "__all__"


class BotSerializer(serializers.ModelSerializer):
    # Dynamically regenerate bot_zip and bot_data urls to point to the API endpoints
    # Otherwise they will point to the front-end download views, which the API client won't
    # be authenticated for.
    bot_zip = serializers.SerializerMethodField()
    bot_data = serializers.SerializerMethodField()
    plays_race = serializers.CharField(source="plays_race.label")

    def get_bot_zip(self, obj):
        # This is_s3_file check is a quick fix to avoid having to figure out how to restructure the storage backend.
        # The parameters in get_file_s3_url_with_content_disposition can only be specified with the S3 backend, else
        # it breaks.
        if is_s3_file(obj.bot_zip):
            return get_file_s3_url_with_content_disposition(obj.bot_zip, f"{obj.name}.zip")
        else:
            p = MatchParticipation.objects.only("participant_number").get(bot=obj, match_id=self.root.instance.id)
            return reverse(
                "match-download-zip",
                kwargs={"pk": self.root.instance.id, "p_num": p.participant_number},
                request=self.context["request"],
            )

    def get_bot_data(self, obj):
        p = (
            MatchParticipation.objects.select_related("bot")
            .only("use_bot_data", "bot__bot_data", "participant_number")
            .get(bot=obj, match_id=self.root.instance.id)
        )
        if p.use_bot_data and p.bot.bot_data:
            # This is_s3_file check is a quick fix to avoid having to figure out how to restructure the storage backend.
            # The parameters in get_file_s3_url_with_content_disposition can only be specified with the S3 backend, else
            # it breaks.
            if is_s3_file(obj.bot_data):
                return get_file_s3_url_with_content_disposition(obj.bot_data, f"{obj.name}_data.zip")
            else:
                return reverse(
                    "match-download-data",
                    kwargs={"pk": self.root.instance.id, "p_num": p.participant_number},
                    request=self.context["request"],
                )
        else:
            return None

    class Meta:
        model = Bot
        fields = (
            "id",
            "name",
            "game_display_id",
            "bot_zip",
            "bot_zip_md5hash",
            "bot_data",
            "bot_data_md5hash",
            "plays_race",
            "type",
        )


class MatchSerializer(serializers.ModelSerializer):
    bot1 = BotSerializer(read_only=True)
    bot2 = BotSerializer(read_only=True)
    map = MapSerializer(read_only=True)

    class Meta:
        model = Match
        fields = ("id", "bot1", "bot2", "map")


class MatchViewSet(viewsets.GenericViewSet):
    """
    MatchViewSet implements a POST method with no field requirements, which will create a match and return the JSON.
    No reading of models is implemented.
    """

    serializer_class = MatchSerializer
    permission_classes = [IsArenaClientOrAdminUser]
    throttle_scope = "arenaclient"
    swagger_schema = None  # exclude this from swagger generation

    def load_participants(self, match: Match):
        match.bot1 = (
            MatchParticipation.objects.select_related("bot")
            .only("bot")
            .get(match_id=match.id, participant_number=1)
            .bot
        )
        match.bot2 = (
            MatchParticipation.objects.select_related("bot")
            .only("bot")
            .get(match_id=match.id, participant_number=2)
            .bot
        )

    def create(self, request, *args, **kwargs):
        no_game_available = cache.get("NoGameAvailable", False)

        if request.user.is_arenaclient:
            match = ACCoordinator.next_match(request.user.arenaclient, no_game_available)
            if match:
                self.load_participants(match)

                serializer = self.get_serializer(match)
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            else:
                cache.set("NoGameAvailable", True, config.GAME_AVAILABLE_CACHE_TIME)

        raise NoGameForClient()

    # todo: check match is in progress/bot is in this match
    @action(detail=True, methods=["GET"], name="Download a participant's zip file", url_path="(?P<p_num>\d+)/zip")
    def download_zip(self, request, *args, **kwargs):
        p = MatchParticipation.objects.get(match=kwargs["pk"], participant_number=kwargs["p_num"])
        if p.bot.can_download_bot_zip(request.user):
            response = HttpResponse(FileWrapper(p.bot.bot_zip), content_type="application/zip")
            response["Content-Disposition"] = f'inline; filename="{p.bot.name}.zip"'
            return response
        else:
            raise PermissionDenied("You cannot download that bot zip.")

    # todo: check match is in progress/bot is in this match
    @action(detail=True, methods=["GET"], name="Download a participant's data file", url_path="(?P<p_num>\d+)/data")
    def download_data(self, request, *args, **kwargs):
        p = MatchParticipation.objects.get(match=kwargs["pk"], participant_number=kwargs["p_num"])
        if p.bot.can_download_bot_data(request.user):
            response = HttpResponse(FileWrapper(p.bot.bot_data), content_type="application/zip")
            response["Content-Disposition"] = f'inline; filename="{p.bot.name}_data.zip"'
            return response
        else:
            raise PermissionDenied("You cannot download that bot data.")


class SubmitResultResultSerializer(serializers.ModelSerializer):
    def validate(self, attrs):
        instance = SubmitResultResultSerializer.Meta.model(**attrs)
        instance.clean()  # enforce model validation
        return attrs

    class Meta:
        model = Result
        fields = "match", "type", "replay_file", "game_steps", "submitted_by", "arenaclient_log"


class SubmitResultBotSerializer(serializers.ModelSerializer):
    class Meta:
        model = Bot
        fields = ("bot_data",)


class SubmitResultParticipationSerializer(serializers.ModelSerializer):
    class Meta:
        model = MatchParticipation
        fields = "avg_step_time", "match_log", "result", "result_cause"


# Front facing serializer used by the view. Combines the other serializers together.
class SubmitResultCombinedSerializer(serializers.Serializer):
    # Result
    match = serializers.IntegerField()
    type = serializers.ChoiceField(choices=Result.TYPES)
    replay_file = serializers.FileField(required=False)
    game_steps = serializers.IntegerField()
    submitted_by = serializers.HiddenField(default=serializers.CurrentUserDefault())
    arenaclient_log = FileField(required=False)
    # Bot
    bot1_data = FileField(required=False)
    bot2_data = FileField(required=False)
    # Participant
    bot1_log = FileField(required=False)
    bot2_log = FileField(required=False)
    bot1_avg_step_time = FloatField(required=False, validators=[validate_not_nan, validate_not_inf])
    bot2_avg_step_time = FloatField(required=False, validators=[validate_not_nan, validate_not_inf])

    # tags
    bot1_tags = serializers.ListField(required=False, child=serializers.CharField(allow_blank=True))
    bot2_tags = serializers.ListField(required=False, child=serializers.CharField(allow_blank=True))


class ResultViewSet(mixins.CreateModelMixin, viewsets.GenericViewSet):
    """
    ResultViewSet implements a POST method to log a result.
    No reading of models is implemented.
    """

    serializer_class = SubmitResultCombinedSerializer
    permission_classes = [IsArenaClientOrAdminUser]
    # Don't throttle result submissions - we can never have "too many" result submissions.
    # throttle_scope = 'arenaclient'
    swagger_schema = None  # exclude this from swagger generation

    def create(self, request, *args, **kwargs):
        if config.LADDER_ENABLED:
            try:
                serializer = self.get_serializer(data=request.data)
                serializer.is_valid(raise_exception=True)

                match_id = serializer.validated_data["match"]

                if config.DEBUG_LOGGING_ENABLED:
                    logger.info(
                        f"Result submission. "
                        f"match: {serializer.validated_data.get('match')} "
                        f"type: {serializer.validated_data.get('type')} "
                        f"replay_file: {serializer.validated_data.get('replay_file')} "
                        f"game_steps: {serializer.validated_data.get('game_steps')} "
                        f"submitted_by: {serializer.validated_data.get('submitted_by')} "
                        f"arenaclient_log: {serializer.validated_data.get('arenaclient_log')} "
                        f"bot1_avg_step_time: {serializer.validated_data.get('bot1_avg_step_time')} "
                        f"bot1_log: {serializer.validated_data.get('bot1_log')} "
                        f"bot1_data: {serializer.validated_data.get('bot1_data')} "
                        f"bot1_tags: {serializer.validated_data.get('bot1_tags')} "
                        f"bot2_avg_step_time: {serializer.validated_data.get('bot2_avg_step_time')} "
                        f"bot2_log: {serializer.validated_data.get('bot2_log')} "
                        f"bot2_data: {serializer.validated_data.get('bot2_data')} "
                        f"bot2_tags: {serializer.validated_data.get('bot2_tags')} "
                    )

                with transaction.atomic():
                    match = Match.objects.prefetch_related(
                        Prefetch("matchparticipation_set", MatchParticipation.objects.all().select_related("bot"))
                    ).get(id=match_id)

                    # validate result
                    result = SubmitResultResultSerializer(
                        data={
                            "match": match_id,
                            "type": serializer.validated_data["type"],
                            "replay_file": serializer.validated_data.get("replay_file"),
                            "game_steps": serializer.validated_data["game_steps"],
                            "submitted_by": serializer.validated_data["submitted_by"].pk,
                            "arenaclient_log": serializer.validated_data.get("arenaclient_log"),
                        }
                    )
                    result.is_valid(raise_exception=True)

                    # validate participants
                    p1_instance = match.matchparticipation_set.get(participant_number=1)
                    result_cause = p1_instance.calculate_result_cause(serializer.validated_data["type"])
                    participant1 = SubmitResultParticipationSerializer(
                        instance=p1_instance,
                        data={
                            "avg_step_time": serializer.validated_data.get("bot1_avg_step_time"),
                            "match_log": serializer.validated_data.get("bot1_log"),
                            "result": p1_instance.calculate_relative_result(serializer.validated_data["type"]),
                            "result_cause": result_cause,
                        },
                        partial=True,
                    )
                    participant1.is_valid(raise_exception=True)

                    p2_instance = match.matchparticipation_set.get(participant_number=2)
                    participant2 = SubmitResultParticipationSerializer(
                        instance=p2_instance,
                        data={
                            "avg_step_time": serializer.validated_data.get("bot2_avg_step_time"),
                            "match_log": serializer.validated_data.get("bot2_log"),
                            "result": p2_instance.calculate_relative_result(serializer.validated_data["type"]),
                            "result_cause": result_cause,
                        },
                        partial=True,
                    )
                    participant2.is_valid(raise_exception=True)

                    # validate bots

                    if not p1_instance.bot.is_in_match(match_id):
                        logger.warning(
                            f"A result was submitted for match {match_id}, "
                            f"which Bot {p1_instance.bot.name} isn't currently in!"
                        )
                        raise APIException(
                            f"Unable to log result: Bot {p1_instance.bot.name} is not currently in this match!"
                        )

                    if not p2_instance.bot.is_in_match(match_id):
                        logger.warning(
                            f"A result was submitted for match {match_id}, "
                            f"which Bot {p2_instance.bot.name} isn't currently in!"
                        )
                        raise APIException(
                            f"Unable to log result: Bot {p2_instance.bot.name} is not currently in this match!"
                        )

                    bot1 = None
                    bot2 = None

                    match_is_requested = match.is_requested
                    # should we update the bot data?
                    if p1_instance.use_bot_data and p1_instance.update_bot_data and not match_is_requested:
                        bot1_data = serializer.validated_data.get("bot1_data")
                        # if we set the bot data key to anything, it will overwrite the existing bot data
                        # so only include bot1_data if it isn't none
                        # Also don't update bot data if it's a requested match.
                        if bot1_data is not None and not match_is_requested:
                            bot1_dict = {"bot_data": bot1_data}
                            bot1 = SubmitResultBotSerializer(instance=p1_instance.bot, data=bot1_dict, partial=True)
                            bot1.is_valid(raise_exception=True)

                    if p2_instance.use_bot_data and p2_instance.update_bot_data and not match_is_requested:
                        bot2_data = serializer.validated_data.get("bot2_data")
                        # if we set the bot data key to anything, it will overwrite the existing bot data
                        # so only include bot2_data if it isn't none
                        # Also don't update bot data if it's a requested match.
                        if bot2_data is not None and not match_is_requested:
                            bot2_dict = {"bot_data": bot2_data}
                            bot2 = SubmitResultBotSerializer(instance=p2_instance.bot, data=bot2_dict, partial=True)
                            bot2.is_valid(raise_exception=True)

                    # save models
                    result = result.save()
                    participant1 = participant1.save()
                    participant2 = participant2.save()
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
                    bot1_tags = parse_tags(serializer.validated_data.get("bot1_tags"))
                    bot2_tags = parse_tags(serializer.validated_data.get("bot2_tags"))
                    # Union tags if both bots belong to the same user
                    if bot1_user == bot2_user:
                        total_tags = list(set(bot1_tags if bot1_tags else []) | set(bot2_tags if bot2_tags else []))

                        if total_tags:
                            total_match_tags = []
                            for tag in total_tags:
                                tag_obj = Tag.objects.get_or_create(name=tag)
                                total_match_tags.append(
                                    MatchTag.objects.get_or_create(tag=tag_obj[0], user=bot1_user)[0]
                                )
                            # remove tags for this match that belong to this user and were not sent in the form
                            match.tags.remove(
                                *match.tags.filter(user=bot1_user).exclude(id__in=[mt.id for mt in total_match_tags])
                            )
                            # add everything, this shouldn't cause duplicates
                            match.tags.add(*total_match_tags)
                    else:
                        if bot1_tags:
                            p1_match_tags = []
                            for tag in bot1_tags:
                                tag_obj = Tag.objects.get_or_create(name=tag)
                                p1_match_tags.append(MatchTag.objects.get_or_create(tag=tag_obj[0], user=bot1_user)[0])
                            # remove tags for this match that belong to this user and were not sent in the form
                            match.tags.remove(
                                *match.tags.filter(user=bot1_user).exclude(id__in=[mt.id for mt in p1_match_tags])
                            )
                            # add everything, this shouldn't cause duplicates
                            match.tags.add(*p1_match_tags)

                        if bot2_tags:
                            p2_match_tags = []
                            for tag in bot2_tags:
                                tag_obj = Tag.objects.get_or_create(name=tag)
                                p2_match_tags.append(MatchTag.objects.get_or_create(tag=tag_obj[0], user=bot2_user)[0])
                            # remove tags for this match that belong to this user and were not sent in the form
                            match.tags.remove(
                                *match.tags.filter(user=bot2_user).exclude(id__in=[mt.id for mt in p2_match_tags])
                            )
                            # add everything, this shouldn't cause duplicates
                            match.tags.add(*p2_match_tags)

                    # Only do these actions if the match is part of a round
                    if result.match.round is not None:
                        result.match.round.update_if_completed()

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

                        if config.ENABLE_ELO_SANITY_CHECK:
                            if config.DEBUG_LOGGING_ENABLED:
                                logger.info("ENABLE_ELO_SANITY_CHECK enabled. Performing check.")

                            # test here to check ELO total and ensure no corruption
                            match_competition = result.match.round.competition
                            expected_elo_sum = (
                                settings.ELO_START_VALUE
                                * CompetitionParticipation.objects.filter(competition=match_competition).count()
                            )
                            actual_elo_sum = CompetitionParticipation.objects.filter(
                                competition=match_competition
                            ).aggregate(Sum("elo"))

                            if actual_elo_sum["elo__sum"] != expected_elo_sum:
                                logger.critical(
                                    f"ELO sum of {actual_elo_sum['elo__sum']} did not match expected value "
                                    f"of {expected_elo_sum} upon submission of result {result.id}"
                                )
                            elif config.DEBUG_LOGGING_ENABLED:
                                logger.info("ENABLE_ELO_SANITY_CHECK passed!")

                        elif config.DEBUG_LOGGING_ENABLED:
                            logger.info("ENABLE_ELO_SANITY_CHECK disabled. Skipping check.")

                        BotStatistics.update_stats_based_on_result(sp1, result, sp2)
                        BotStatistics.update_stats_based_on_result(sp2, result, sp1)

                        if result.is_crash_or_timeout:
                            run_consecutive_crashes_check(result.get_causing_participant_of_crash_or_timeout_result)

                headers = self.get_success_headers(serializer.data)
                return Response({"result_id": result.id}, status=status.HTTP_201_CREATED, headers=headers)
            except Exception:
                logger.exception("Exception while processing result submission")
                raise
        else:
            raise LadderDisabled()

    # todo: use a model form
    # todo: avoid results being logged against matches not owned by the submitter


class SetArenaClientStatusSerializer(serializers.ModelSerializer):
    class Meta:
        model = ArenaClientStatus
        fields = ("status",)


class SetArenaClientStatusViewSet(mixins.CreateModelMixin, viewsets.GenericViewSet):
    """
    SetArenaClientStatusViewSet implements a POST method to record an arena client's status.
    No reading of models is implemented.
    """

    serializer_class = SetArenaClientStatusSerializer
    permission_classes = [IsArenaClient]
    swagger_schema = None  # exclude this from swagger generation

    def perform_create(self, serializer):
        serializer.save(arenaclient=self.request.user.arenaclient)


def run_consecutive_crashes_check(triggering_participant: MatchParticipation):
    """
    Checks to see whether the last X results for a participant are crashes and, if so, disables the bot
    and sends an alert to the bot author
    :param triggering_participant: The participant who triggered this check and whose bot we should run the check for.
    :return:
    """

    if config.BOT_CONSECUTIVE_CRASH_LIMIT < 1:
        return  # Check is disabled

    if not triggering_participant.bot.competition_participations.filter(active=True).exists():
        return  # No use running the check - bot is already inactive.

    # Get recent match participation records for this bot
    recent_participations = MatchParticipation.objects.filter(
        bot=triggering_participant.bot, match__result__isnull=False
    ).order_by("-match__result__created")[: config.BOT_CONSECUTIVE_CRASH_LIMIT]

    # if there's not enough participations yet, then exit without action
    if recent_participations.count() < config.BOT_CONSECUTIVE_CRASH_LIMIT:
        return

    # if any of the previous results weren't a crash or already triggered a crash limit alert, then exit without action
    for recent_participation in recent_participations:
        if not recent_participation.crashed:
            return
        elif recent_participation.triggered_a_crash_limit_alert:
            return

    # Log a crash alert
    BotCrashLimitAlert.objects.create(triggering_match_participation=triggering_participant)

    # If we get to here, all the results were crashes, so take action
    # REMOVED UNTIL WE DECIDE TO USE THIS
    # Bots.disable_and_send_crash_alert(triggering_participant.bot)
