import logging
import random

from django.db import transaction
from django.db.models import Count
from django.utils import timezone

from constance import config
from rest_framework.exceptions import APIException

from aiarena.api.arenaclient.exceptions import (
    CompetitionClosing,
    CompetitionPaused,
    MaxActiveRounds,
    NoMaps,
    NotEnoughAvailableBots,
)
from aiarena.core.api import Bots
from aiarena.core.api.competitions import Competitions
from aiarena.core.api.maps import Maps
from aiarena.core.models import (
    ArenaClient,
    Bot,
    Competition,
    CompetitionParticipation,
    Map,
    Match,
    MatchParticipation,
    Result,
    Round,
)
from aiarena.core.models.game_mode import GameMode


logger = logging.getLogger(__name__)


class Matches:
    @staticmethod
    def cancel(match_id):
        try:
            with transaction.atomic():
                match = Match.objects.select_for_update().get(pk=match_id)
                result = match.cancel(None)
                if result == Match.CancelResult.MATCH_DOES_NOT_EXIST:  # should basically not happen, but just in case
                    raise Exception('Match "%s" does not exist' % match_id)
                elif result == Match.CancelResult.RESULT_ALREADY_EXISTS:
                    raise Exception('A result already exists for match "%s"' % match_id)
        except Match.DoesNotExist:
            raise Exception('Match "%s" does not exist' % match_id)

    @staticmethod
    def request_match(user, bot, opponent, map: Map = None, game_mode: GameMode = None):
        # if map is none, a game mode must be supplied and a random map gets chosen
        if map is None:
            if game_mode:
                map = Maps.random_of_game_mode(game_mode)
            else:
                map = Map.objects.first()  # maybe improve this logic,  perhaps a random map and not just the first one
        return Match.create(
            None,
            map,
            bot,
            opponent,
            user,
            bot1_update_data=False,
            bot2_update_data=False,
            require_trusted_arenaclient=False,
        )

    # todo: have arena client check in with web service in order to delay this
    @staticmethod
    def timeout_overtime_bot_games():
        matches_without_result = (
            Match.objects.only("round")
            .select_for_update(of=("self",))
            .select_related("round")
            .filter(first_started__lt=timezone.now() - config.TIMEOUT_MATCHES_AFTER, result__isnull=True)
        )
        for match in matches_without_result:
            Result.objects.create(match=match, type="MatchCancelled", game_steps=0)
            if match.round is not None:  # if the match is part of a round, check for round completion
                match.round.update_if_completed()

    @staticmethod
    def start_match(match: Match, arenaclient: ArenaClient) -> bool:
        # Allowing the match to be played on a untrusted client if the user allows the download after requesting a match.
        require_trusted_arenaclient = match.require_trusted_arenaclient
        if not require_trusted_arenaclient:
            bot1 = match.participant1.bot
            bot2 = match.participant2.bot
            require_trusted_arenaclient = (
                not bot1.bot_zip_publicly_downloadable
                or not bot2.bot_zip_publicly_downloadable
                or not bot1.bot_data_publicly_downloadable
                or not bot2.bot_data_publicly_downloadable
            )
        if require_trusted_arenaclient and not arenaclient.trusted:
            return False
        match.lock_me()  # lock self to avoid race conditions
        if match.started is None:
            # Avoid starting a match when a participant is not available
            participations = MatchParticipation.objects.raw(
                """
                SELECT cm.id FROM core_matchparticipation cm
                where ((cm.use_bot_data or cm.update_bot_data) or cm.bot_id not in (
                        select bot_id
                        from core_matchparticipation
                        inner join core_match m on core_matchparticipation.match_id = m.id
                        left join core_result cr on m.id = cr.match_id
                        where m.started is not null
                        and cr.type is null
                        and (core_matchparticipation.use_bot_data  or core_matchparticipation.update_bot_data)       
                        and m.id != %s 
                    )) and match_id = %s

            """,
                (match.id, match.id),
            )

            if len(participations) < 2:
                # Todo: Commented out to avoid log spam. This used to be a last second sanity check.
                # Todo: Investigate whether it is still the case or whether this is no longer considered a system fault
                # Todo: worthy of a warning message being logged.
                # logger.warning(f"Match {match.id} failed to start unexpectedly"
                #                f" because one of the participants was not available.")
                return False

            if match.round:  # if this is a ladder match, record the starting elo
                for p in participations:
                    p.starting_elo = (
                        p.bot.competition_participations.only("elo", "bot_id")
                        .get(competition=match.round.competition)
                        .elo
                    )
                    p.save()

            now = timezone.now()
            match.started = now
            match.first_started = now
            match.assigned_to = arenaclient
            match.save()
            return True
        else:
            logger.warning(f"Match {match.id} failed to start unexpectedly as it was already started.")
            return False

    @staticmethod
    def attempt_to_start_a_requested_match(requesting_ac: ArenaClient):
        # Try get a requested match
        # Do we want trusted clients to run games not requiring trusted clients?
        matches = (
            Match.objects.select_related("round")
            .only("started", "assigned_to", "round")
            .filter(started__isnull=True, requested_by__isnull=False)
            .select_for_update(of=("self",))
            .order_by("created")
        )
        if matches.count() > 0:
            return Matches._start_and_return_a_match(requesting_ac, matches)
        else:
            return None

    @staticmethod
    def _start_and_return_a_match(requesting_ac: ArenaClient, matches):
        for match in matches:
            if Matches.start_match(match, requesting_ac):
                return match
        return None  # No match was able to start

    @staticmethod
    def _attempt_to_start_a_ladder_match(requesting_ac: ArenaClient, for_round):
        if for_round is not None:
            ladder_matches_to_play = list(
                Match.objects.raw(
                    """
            SELECT core_match.id, core_match.started, assigned_to_id, round_id from core_match
            inner join core_round cr on core_match.round_id = cr.id
            where core_match.started is null and requested_by_id is null and round_id = %s
            order by round_id
            for update 
            """,
                    (for_round.id,),
                )
            )

        else:
            ladder_matches_to_play = list(
                Match.objects.raw(
                    """
                SELECT core_match.id, core_match.started, assigned_to_id, round_id from core_match
                inner join core_round cr on core_match.round_id = cr.id
                where core_match.started is null and requested_by_id is null 
                order by round_id
                for update 
                """
                )
            )

        if len(ladder_matches_to_play) > 0:
            bots_with_a_ladder_match_to_play = Bot.objects.raw(
                """
                SELECT DISTINCT CB.ID
                    FROM CORE_MATCH CM
                    INNER JOIN CORE_MATCHPARTICIPATION C ON CM.ID = C.MATCH_ID
                    INNER JOIN CORE_BOT CB ON C.BOT_ID = CB.ID
                WHERE CM.STARTED IS NULL
                        AND REQUESTED_BY_ID IS NULL
                        AND C.BOT_ID not in
                            (SELECT CB.ID
                                FROM CORE_MATCHPARTICIPATION
                                INNER JOIN CORE_MATCH M ON CORE_MATCHPARTICIPATION.MATCH_ID = M.ID
                                LEFT JOIN CORE_RESULT CR ON M.ID = CR.MATCH_ID
                                INNER JOIN CORE_BOT CB ON CORE_MATCHPARTICIPATION.BOT_ID = CB.ID
                            WHERE M.STARTED IS NOT NULL
                                    AND CR.ID IS NULL
                                    AND CORE_MATCHPARTICIPATION.USE_BOT_DATA
                                    AND CORE_MATCHPARTICIPATION.UPDATE_BOT_DATA )  

            """
            )
            match_ids = [match.id for match in ladder_matches_to_play]
            bot_ids = [bot.id for bot in bots_with_a_ladder_match_to_play]

            available_ladder_matches_to_play = (
                list(
                    Match.objects.raw(
                        """
                    SELECT cm.* from core_match cm
                    inner join core_matchparticipation c1 on cm.id = c1.match_id and c1.participant_number = 1
                    inner join core_matchparticipation c2 on cm.id = c2.match_id and c2.participant_number = 2
                    where cm.id in %s
                    and c1.bot_id in %s and c2.bot_id in %s
            """,
                        (tuple(match_ids), tuple(bot_ids), tuple(bot_ids)),
                    )
                )
                if bot_ids
                else []
            )

            random.shuffle(available_ladder_matches_to_play)  # ensure the match selection is random

            # if, out of the bots that have a ladder match to play, at least 2 are active, then try starting matches.
            if Bots.available_is_more_than(bots_with_a_ladder_match_to_play, 2):
                return Matches._start_and_return_a_match(requesting_ac, available_ladder_matches_to_play)
        return None

    @staticmethod
    def _attempt_to_generate_new_round(competition: Competition):
        active_maps = Map.objects.filter(
            competitions__in=[
                competition,
            ]
        ).select_for_update()
        if active_maps.count() == 0:
            raise NoMaps()

        if competition.is_paused:
            raise CompetitionPaused()
        if competition.is_closing:  # we should technically never hit this
            raise CompetitionClosing()

        new_round = Round.objects.create(competition=competition)
        if competition.rounds_this_cycle >= competition.rounds_per_cycle:
            competition.rounds_this_cycle = 1
        else:
            competition.rounds_this_cycle += 1

        # Update divisions
        # Does not split on the first cycle of every competition so initial participants can be accuarately ranked
        if competition.rounds_this_cycle == 1:
            # Get match counts to determine which bots are still in placements
            match_counts = list(
                MatchParticipation.objects.filter(match__result__isnull=False, match__round__competition=competition)
                .exclude(match__result__type__in=["MatchCancelled", "InitializationError", "Error"])
                .values("bot")
                .annotate(match_count=Count("bot"))
            )
            match_counts = {vs["bot"]: vs["match_count"] for vs in match_counts}
            # Order bots out of placement by elo, order bots in placement by games played
            all_participants = (
                CompetitionParticipation.objects.only("id", "bot__id", "division_num", "elo", "match_count")
                .filter(competition=competition, active=True)
                .order_by("elo")
            )
            if competition.n_placements <= 0:
                existing_participants = list(all_participants)
                placement_participants = []
            else:
                existing_participants = sorted(
                    all_participants.filter(
                        bot__id__in=[k for k, v in match_counts.items() if v >= competition.n_placements]
                    ),
                    key=lambda p: p.elo,
                )
                placement_participants = sorted(
                    all_participants.exclude(bot__id__in=[p.bot.id for p in existing_participants]),
                    key=lambda p: (match_counts[p.bot.id] if p.bot.id in match_counts else 0, -p.elo),
                    reverse=True,
                )
            active_participants = placement_participants + existing_participants
            n_active_participants = len(active_participants)
            # Update number of divisions
            if competition.should_split_divisions(n_active_participants) or competition.should_merge_divisions(
                n_active_participants
            ):
                if new_round.number > 1 and n_active_participants > competition.target_division_size:
                    # Limit to target so that if lots join at once it doesn't overshoot
                    competition.n_divisions = min(
                        competition.target_n_divisions, n_active_participants // competition.target_division_size
                    )
                else:
                    competition.n_divisions = 1
            # Update bot division numbers
            updated_participants = []
            div_size, rem = divmod(n_active_participants, competition.n_divisions)
            divs = [
                active_participants[i * div_size + min(i, rem) : (i + 1) * div_size + min(i + 1, rem)]
                for i in range(competition.n_divisions)
            ]
            current_div_num = competition.n_divisions - 1 + CompetitionParticipation.MIN_DIVISION
            for d in divs:
                for p in d:
                    updated_participants.append(p)
                    p.division_num = current_div_num
                    p.match_count = match_counts[p.bot.id] if p.bot.id in match_counts else 0
                    p.in_placements = p.match_count < competition.n_placements
                current_div_num -= 1
            CompetitionParticipation.objects.bulk_update(
                updated_participants, ["division_num", "in_placements", "match_count"]
            )
        competition.save()

        # Get updated participants
        active_participants = CompetitionParticipation.objects.only("id", "division_num", "bot").filter(
            competition=competition, active=True, division_num__gte=CompetitionParticipation.MIN_DIVISION
        )
        already_processed_participants = []
        # loop through and generate matches for all active participants
        for participant1 in active_participants:
            already_processed_participants.append(participant1.id)
            active_participants_in_div = (
                CompetitionParticipation.objects.only("bot")
                .filter(competition=competition, active=True, division_num=participant1.division_num)
                .exclude(id__in=already_processed_participants)
            )
            for participant2 in active_participants_in_div:
                Match.create(
                    new_round,
                    random.choice(active_maps),
                    participant1.bot,
                    participant2.bot,
                    require_trusted_arenaclient=competition.require_trusted_infrastructure,
                )

        # Pre-list the IDs to get around this while on mariadb: https://code.djangoproject.com/ticket/28787
        p_ids = [p.id for p in active_participants]
        CompetitionParticipation.objects.filter(competition=competition).exclude(id__in=p_ids).update(
            participated_in_most_recent_round=False
        )
        active_participants.update(participated_in_most_recent_round=True)

        return new_round

    @staticmethod
    def start_next_match_for_competition(requesting_ac: ArenaClient, competition: Competition):
        # LADDER MATCHES
        # Get rounds with un-started matches
        # The "IN" is a workaround due to postgresql not allowing "FOR UPDATE" with a DISTINCT clause
        rounds = Round.objects.raw(
            """
            SELECT 
                cr.id 
            FROM 
                core_round cr 
            WHERE 
                cr.id IN (
                    SELECT 
                        cr.id 
                    FROM 
                        core_round cr 
                        INNER JOIN core_match cm ON cr.id = cm.round_id 
                    WHERE 
                        competition_id=%s 
                    AND finished IS NULL 
                    AND cm.started IS NULL 
                    ORDER BY NUMBER
                ) for update""",
            (competition.id,),
        )

        for round in rounds:
            match = Matches._attempt_to_start_a_ladder_match(requesting_ac, round)
            if match is not None:
                return match  # a match was found - we're done

        # If none of the previous matches were able to start, and we don't have 2 active bots available,
        # then we give up.
        # todo: does this need to be a select_for_update?
        active_bots = Competitions.get_active_bots(competition).select_for_update()
        if not Bots.available_is_more_than(active_bots, 2):
            raise NotEnoughAvailableBots()

        # If we get to here, then we have
        # - no matches from any existing round we can start
        # - at least 2 active bots available for play

        if Competitions.has_reached_maximum_active_rounds(competition):
            raise MaxActiveRounds()
        else:  # generate new round
            round = Matches._attempt_to_generate_new_round(competition)
            match = Matches._attempt_to_start_a_ladder_match(requesting_ac, round)
            if match is None:
                raise APIException("Failed to start match. There might not be any available participants.")
            else:
                return match
