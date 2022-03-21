import logging
import random
from enum import Enum

from constance import config
from django.db import transaction
from django.utils import timezone
from django.db.models import Count
from rest_framework.exceptions import APIException

from aiarena.api.arenaclient.exceptions import NotEnoughAvailableBots, MaxActiveRounds, NoMaps, CompetitionPaused, \
    CompetitionClosing
from aiarena.core.api import Bots
from aiarena.core.api.competitions import Competitions
from aiarena.core.api.maps import Maps
from aiarena.core.models import Result, Map, Match, Round, Bot, User, MatchParticipation, Competition, \
    CompetitionParticipation, ArenaClient
from aiarena.core.models.game_mode import GameMode

logger = logging.getLogger(__name__)


class Matches:
    @staticmethod
    def request_match(user, bot, opponent, map: Map=None, game_mode: GameMode=None):
        # if map is none, a game mode must be supplied and a random map gets chosen
        if map is None:
            if game_mode:
                map = Maps.random_of_game_mode(game_mode)
            else:
                map = Map.objects.first() # maybe improve this logic,  perhaps a random map and not just the first one
        return Match.create(None, map, bot,
                            opponent,
                            user, bot1_update_data=False, bot2_update_data=False, require_trusted_arenaclient=False)

    # todo: have arena client check in with web service in order to delay this
    @staticmethod
    def timeout_overtime_bot_games():
        matches_without_result = Match.objects.only('round').select_related('round').select_for_update().filter(
            started__lt=timezone.now() - config.TIMEOUT_MATCHES_AFTER, result__isnull=True)
        for match in matches_without_result:
            Result.objects.create(match=match, type='MatchCancelled', game_steps=0)
            if match.round is not None:  # if the match is part of a round, check for round completion
                match.round.update_if_completed()

    @staticmethod
    def start_match(match, assign_to) -> bool:
        if match.require_trusted_arenaclient and not assign_to.trusted:
            return False
        match.lock_me()  # lock self to avoid race conditions
        if match.started is None:
            # Avoid starting a match when a participant is not available
            participations = MatchParticipation.objects.raw("""
                SELECT cm.id FROM core_matchparticipation cm
                where ((cm.use_bot_data =0 or cm.update_bot_data =0) or cm.bot_id not in (
                        select bot_id
                        from core_matchparticipation
                        inner join core_match m on core_matchparticipation.match_id = m.id
                        left join core_result cr on m.id = cr.match_id
                        where m.started is not null
                        and cr.type is null
                        and (core_matchparticipation.use_bot_data = 1 or core_matchparticipation.update_bot_data =1)       
                        and m.id != %s 
                    )) and match_id = %s

            """, (match.id, match.id))

            if len(participations) < 2:
                # Todo: Commented out to avoid log spam. This used to be a last second sanity check.
                # Todo: Investigate whether it is still the case or whether this is no longer considered a system fault
                # Todo: worthy of a warning message being logged.
                # logger.warning(f"Match {match.id} failed to start unexpectedly"
                #                f" because one of the participants was not available.")
                return False

            if match.round:  # if this is a ladder match, record the starting elo
                for p in participations:
                    p.starting_elo = p.bot.competition_participations.only('elo', 'bot_id') \
                        .get(competition=match.round.competition).elo
                    p.save()

            match.started = timezone.now()
            match.assigned_to = assign_to
            match.save()
            return True
        else:
            logger.warning(f"Match {match.id} failed to start unexpectedly as it was already started.")
            return False

    @staticmethod
    def attempt_to_start_a_requested_match(requesting_client: ArenaClient):
        # Try get a requested match
        # Do we want trusted clients to run games not requiring trusted clients?
        matches = Match.objects.select_related('round').only('started', 'assigned_to', 'round') \
            .filter(started__isnull=True, requested_by__isnull=False).select_for_update().order_by('created')
        if matches.count() > 0:
            return Matches._start_and_return_a_match(requesting_client, matches)
        else:
            return None

    @staticmethod
    def _start_and_return_a_match(requesting_client: ArenaClient, matches):
        for match in matches:
            if Matches.start_match(match, requesting_client):
                return match
        return None  # No match was able to start

    @staticmethod
    def _attempt_to_start_a_ladder_match(requesting_user: User, for_round):
        if for_round is not None:
            ladder_matches_to_play = list(Match.objects.raw("""
            SELECT core_match.id, core_match.started, assigned_to_id, round_id from core_match
            inner join core_round cr on core_match.round_id = cr.id
            where core_match.started is null and requested_by_id is null and round_id = %s
            order by round_id
            for update 
            """, (for_round.id,)))

        else:
            ladder_matches_to_play = list(Match.objects.raw("""
                SELECT core_match.id, core_match.started, assigned_to_id, round_id from core_match
                inner join core_round cr on core_match.round_id = cr.id
                where core_match.started is null and requested_by_id is null 
                order by round_id
                for update 
                """))

        if len(ladder_matches_to_play) > 0:
            bots_with_a_ladder_match_to_play = Bot.objects.raw("""
            select distinct cb.id
              from core_match cm
             inner join core_matchparticipation c
                on cm.id = c.match_id
            inner join core_bot cb on c.bot_id = cb.id
             where cm.started is null
               and requested_by_id is null
               and c.bot_id not in 
                    (select cb.id
                      from core_matchparticipation
                     inner join core_match m
                        on core_matchparticipation.match_id = m.id
                      left join core_result cr
                        on m.id = cr.match_id
                    inner join core_bot cb on core_matchparticipation.bot_id = cb.id
                     where m.started is not null
                       and cr.id is null
                       and core_matchparticipation.use_bot_data = 1
                       and core_matchparticipation.update_bot_data =1    )               
                for update         
            """)
            match_ids = [match.id for match in ladder_matches_to_play]
            bot_ids = [bot.id for bot in bots_with_a_ladder_match_to_play]

            available_ladder_matches_to_play = list(Match.objects.raw("""
                    SELECT cm.* from core_match cm
                    inner join core_matchparticipation c1 on cm.id = c1.match_id and c1.participant_number = 1
                    inner join core_matchparticipation c2 on cm.id = c2.match_id and c2.participant_number = 2
                    where cm.id in %s
                    and c1.bot_id in %s and c2.bot_id in %s
            """, (tuple(match_ids), tuple(bot_ids), tuple(bot_ids)))) if bot_ids else []

            random.shuffle(available_ladder_matches_to_play)  # ensure the match selection is random
            # if, out of the bots that have a ladder match to play, at least 2 are active, then try starting matches.
            if len(Bots.get_available(bots_with_a_ladder_match_to_play)) >= 2:
                return Matches._start_and_return_a_match(requesting_user, available_ladder_matches_to_play)
        return None

    @staticmethod
    def _attempt_to_generate_new_round(competition: Competition):
        active_maps = Map.objects.filter(competitions__in=[competition, ]).select_for_update()
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
            match_counts = list(MatchParticipation.objects
                .filter(match__result__isnull=False,  match__round__competition=competition)
                .exclude(match__result__type__in=['MatchCancelled', 'InitializationError', 'Error'])
                .values('bot')
                .annotate(match_count = Count('bot')))
            match_counts = { vs['bot']:vs['match_count'] for vs in match_counts }
            # Order bots out of placement by elo, order bots in placement by games played
            all_participants = (CompetitionParticipation.objects
                .only("id","bot__id","division_num","elo","match_count")
                .filter(competition=competition, active=True)
                .order_by('elo'))
            if competition.n_placements <= 0:
                existing_participants = list(all_participants)
                placement_participants = []
            else:
                existing_participants = sorted(
                    all_participants.filter(bot__id__in=[k for k, v in match_counts.items() if v >= competition.n_placements]),
                    key=lambda p: p.elo)
                placement_participants = sorted(
                    all_participants.exclude(bot__id__in=[p.bot.id for p in existing_participants]), 
                    key=lambda p: (match_counts[p.bot.id] if p.bot.id in match_counts else 0, -p.elo),
                    reverse=True)
            active_participants =  placement_participants + existing_participants
            n_active_participants = len(active_participants)
            # Update number of divisions
            if competition.should_split_divisions(n_active_participants) or competition.should_merge_divisions(n_active_participants):
                if new_round.number > 1 and n_active_participants > competition.target_division_size:
                    # Limit to target so that if lots join at once it doesn't overshoot
                    competition.n_divisions = min(competition.target_n_divisions, n_active_participants // competition.target_division_size)
                else:
                    competition.n_divisions = 1
            # Update bot division numbers
            updated_participants = []
            div_size, rem = divmod(n_active_participants, competition.n_divisions)
            divs = [active_participants[i*div_size+min(i, rem):(i+1)*div_size+min(i+1, rem)] for i in range(competition.n_divisions)]
            current_div_num = competition.n_divisions - 1 + CompetitionParticipation.MIN_DIVISION
            for d in divs:
                for p in d:
                    updated_participants.append(p)
                    p.division_num = current_div_num
                    p.match_count = match_counts[p.bot.id] if p.bot.id in match_counts else 0
                    p.in_placements = p.match_count < competition.n_placements
                current_div_num -= 1
            CompetitionParticipation.objects.bulk_update(updated_participants, ['division_num', 'in_placements', 'match_count'])
        competition.save()
        
        # Get updated participants
        active_participants = (CompetitionParticipation.objects
            .only("id","division_num","bot")
            .filter(competition=competition, active=True, division_num__gte=CompetitionParticipation.MIN_DIVISION))
        already_processed_participants = []
        # loop through and generate matches for all active participants
        for participant1 in active_participants:
            already_processed_participants.append(participant1.id)
            active_participants_in_div = (CompetitionParticipation.objects
                .only("bot")
                .filter(competition=competition, active=True, division_num=participant1.division_num)
                .exclude(id__in=already_processed_participants))
            for participant2 in active_participants_in_div:
                Match.create(new_round, random.choice(active_maps), participant1.bot, participant2.bot, require_trusted_arenaclient=True)

        return new_round

    @staticmethod
    def start_next_match_for_competition(requesting_user, competition: Competition):
        # LADDER MATCHES
        # Get rounds with un-started matches
        rounds = Round.objects.raw("""
            SELECT distinct cr.id from core_round cr 
            inner join core_match cm on cr.id = cm.round_id
            where competition_id=%s
            and finished is null
            and cm.started is null
            order by number
            for update""", (competition.id,))

        for round in rounds:
            match = Matches._attempt_to_start_a_ladder_match(requesting_user, round)
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
            match = Matches._attempt_to_start_a_ladder_match(requesting_user, round)
            if match is None:
                raise APIException("Failed to start match. There might not be any available participants.")
            else:
                return match
