import logging
import random
from enum import Enum

from constance import config
from django.db import transaction
from django.utils import timezone
from rest_framework.exceptions import APIException

from aiarena.api.arenaclient.exceptions import NotEnoughAvailableBots, MaxActiveRounds, NoMaps, CurrentSeasonPaused, \
    CurrentSeasonClosing
from aiarena.core.api import Bots
from aiarena.core.models import Result, Map, Match, Round, Bot, User, MatchParticipation, Season

logger = logging.getLogger(__name__)


class Matches:
    @staticmethod
    def request_match(user, bot, opponent=None, map=None):
        # if opponent or map is none, a random one gets chosen
        return Match.create(None, map if map is not None else Map.random_active(), bot,
                            opponent if opponent is not None else bot.get_random_active_excluding_self(),
                            user, bot1_update_data=False, bot2_update_data=False)

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
        match.lock_me()  # lock self to avoid race conditions
        if match.started is None:
            # Avoid starting a match when a participant is not available
            participations = MatchParticipation.objects.only('id')\
                .select_for_update().filter(match=match)
            for p in participations:
                if not p.available_to_start_match:
                    logger.warning(f"Match {match.id} failed to start unexpectedly"
                                   f" because participant {p.bot.name} was not available.")
                    return False

            if match.round:  # if this is a ladder match, record the starting elo
                for p in participations:
                    p.starting_elo = p.bot.seasonparticipation_set.only('elo', 'bot_id')\
                        .get(season=Season.get_current_season()).elo
                    p.save()

            match.started = timezone.now()
            match.assigned_to = assign_to
            match.save()
            return True
        else:
            logger.warning(f"Match {match.id} failed to start unexpectedly as it was already started.")
            return False

    @staticmethod
    def _attempt_to_start_a_requested_match(requesting_user: User):
        # Try get a requested match
        matches = Match.objects.select_related('round').only('started', 'assigned_to', 'round') \
            .filter(started__isnull=True, requested_by__isnull=False).select_for_update().order_by('created')
        if matches.count() > 0:
            return Matches._start_and_return_a_match(requesting_user, matches)
        else:
            return None

    @staticmethod
    def _start_and_return_a_match(requesting_user: User, matches: list):
        for match in matches:
            if Matches.start_match(match, requesting_user):
                return match
        return None  # No match was able to start

    @staticmethod
    def _attempt_to_start_a_ladder_match(requesting_user: User, for_round):
        if for_round is not None:
            ladder_matches_to_play = Match.objects.select_related('round').prefetch_related('matchparticipation_set')\
                .only('started', 'assigned_to', 'round')\
                .filter(started__isnull=True, requested_by__isnull=True, round=for_round)\
                .select_for_update().order_by('round_id')
        else:
            ladder_matches_to_play = Match.objects.select_related('round').prefetch_related('matchparticipation_set')\
                .only('started', 'assigned_to', 'round')\
                .filter(started__isnull=True, requested_by__isnull=True)\
                .select_for_update().order_by('round_id')
        if ladder_matches_to_play.count() > 0:
            participants_of_ladder_matches_to_play = []
            [participants_of_ladder_matches_to_play.extend(m.matchparticipation_set.all()) for m in
             ladder_matches_to_play]
            list_of_ladder_matches_to_play = list(ladder_matches_to_play)
            random.shuffle(list_of_ladder_matches_to_play) # pick a random one
            bots_with_a_ladder_match_to_play = Bot.objects.only('id').filter(
                matchparticipation__in=participants_of_ladder_matches_to_play).select_for_update()

            # if, out of the bots that have a ladder match to play, at least 2 are active, then try starting matches.
            if Bots.available_is_more_than(bots_with_a_ladder_match_to_play, 2):
                return Matches._start_and_return_a_match(requesting_user, list_of_ladder_matches_to_play)
        return None

    @staticmethod
    def _attempt_to_generate_new_round(for_season: Season):
        active_maps = Map.objects.filter(active=True).select_for_update()
        if active_maps.count() == 0:
            raise NoMaps()

        if for_season.is_paused:
            raise CurrentSeasonPaused()
        if for_season.is_closing:  # we should technically never hit this
            raise CurrentSeasonClosing()

        new_round = Round.objects.create(season=for_season)

        active_bots = Bot.objects.only("id").filter(active=True)
        already_processed_bots = []

        # loop through and generate matches for all active bots
        for bot1 in active_bots:
            already_processed_bots.append(bot1.id)
            for bot2 in Bot.objects.only("id").filter(active=True).exclude(id__in=already_processed_bots):
                Match.create(new_round, random.choice(active_maps), bot1, bot2)

        return new_round

    @staticmethod
    def start_next_match(requesting_user):
        with transaction.atomic():
            # REQUESTED MATCHES
            match = Matches._attempt_to_start_a_requested_match(requesting_user)
            if match is not None:
                return match  # a match was found - we're done

            # LADDER MATCHES
            current_season = Season.get_current_season()
            # Get rounds with un-started matches
            rounds = Round.objects.only('id').filter(season=current_season,
                                          finished__isnull=True,
                                          match__started__isnull=True).select_for_update().order_by('number')
            for round in rounds:
                match = Matches._attempt_to_start_a_ladder_match(requesting_user, round)
                if match is not None:
                    return match  # a match was found - we're done

            # If none of the previous matches were able to start, and we don't have 2 active bots available,
            # then we give up.
            active_bots = Bot.objects.only("id").filter(active=True).select_for_update()
            if not Bots.available_is_more_than(active_bots, 2):
                raise NotEnoughAvailableBots()

            # If we get to here, then we have
            # - no matches from any existing round we can start
            # - at least 2 active bots available for play

            if Round.max_active_rounds_reached():
                raise MaxActiveRounds()
            else:  # generate new round
                round = Matches._attempt_to_generate_new_round(current_season)
                match = Matches._attempt_to_start_a_ladder_match(requesting_user, round)
                if match is None:
                    raise APIException("Failed to start match. There might not be any available participants.")
                else:
                    return match
