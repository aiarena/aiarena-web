import logging

from constance import config
from django.db import transaction, connection
from django.db.models import F
from django.utils import timezone
from rest_framework.exceptions import APIException
from wiki.models import Article
from aiarena.core.models import Bot, Result, Round, Map, Season, MatchParticipation, Match
from aiarena.api.arenaclient.exceptions import NotEnoughAvailableBots, MaxActiveRounds
from aiarena.core.api import Bots

logger = logging.getLogger(__name__)


class Matches:
    @staticmethod
    def request_match(bot, opponent=None, map=None, user=None):
        # if opponent or map is none, a random one gets chosen
        return Match.create(None, map if map is not None else Map.random_active(), bot,
                            opponent if opponent is not None else bot.get_random_active_excluding_self(),
                            user, bot1_update_data=False, bot2_update_data=False)


    @staticmethod
    def _locate_and_return_started_match(requesting_user):
        # todo: apparently order_by('?') is really slow
        # https://stackoverflow.com/questions/962619/how-to-pull-a-random-record-using-djangos-orm#answer-962672
        # Wrapping the model call here in list() fixes the ordering not being applied.
        # Probably due to Django's lazy evaluation - it forces evaluation thus ensuring the order by is processed
        for match in list(
                Match.objects.filter(started__isnull=True).order_by(F('round_id').asc(nulls_last=False), '?')):
            start_result = match.start(requesting_user)
            if start_result == Match.StartResult.SUCCESS:
                return match
            elif start_result == Match.StartResult.FAIL_ALREADY_STARTED:
                logger.warning(f"Match {match.id} failed to start unexpectedly as it was already started.")

        return None

    # todo: have arena client check in with web service inorder to delay this
    @staticmethod
    def timeout_overtime_bot_games():
        matches_without_result = Match.objects.select_related('round').select_for_update().filter(
            started__lt=timezone.now() - config.TIMEOUT_MATCHES_AFTER, result__isnull=True)
        for match in matches_without_result:
            Result.objects.create(match=match, type='MatchCancelled', game_steps=0)
            if match.round is not None:  # if the match is part of a round, check for round completion
                match.round.update_if_completed()

    @staticmethod
    def start_next_match(requesting_user):
        # todo: clean up this whole section

        with connection.cursor() as cursor:
            # Lock the matches table
            # this needs to happen so that if we end up having to generate a new set of matches
            # then we don't hit a race condition
            # MySql also requires we lock any other tables we access as well.
            cursor.execute(
                "LOCK TABLES {} WRITE, {} WRITE, {} WRITE, {} WRITE, {} READ, {} READ, {} READ".format(
                    Match._meta.db_table,
                    Round._meta.db_table,
                    MatchParticipation._meta.db_table,
                    Bot._meta.db_table,
                    Map._meta.db_table,
                    Article._meta.db_table,
                    Season._meta.db_table))
            try:
                match = Matches._locate_and_return_started_match(requesting_user)
                if match is None:
                    if len(Bots.get_active_and_available()) < 2:
                        # All the active bots are already in a match
                        raise NotEnoughAvailableBots()
                    elif Round.max_active_rounds_reached():
                        raise MaxActiveRounds()
                    else:  # generate new round
                        Round.generate_new()
                        match = Matches._locate_and_return_started_match(requesting_user)
                        if match is None:
                            cursor.execute("ROLLBACK")
                            raise APIException("Failed to start match. There might not be any available participants.")
                        else:
                            return match
                else:
                    return match
            except:
                # ROLLBACK here so the UNLOCK statement doesn't commit changes
                cursor.execute("ROLLBACK")
                raise  # rethrow
            finally:
                # pass
                cursor.execute("UNLOCK TABLES;")
