import logging

from constance import config
from django.db import transaction, connection
from django.utils import timezone
from wiki.models import Article
from aiarena.core.models import Bot, Result, Round, Map, Season, MatchParticipation, Match
from aiarena.api.arenaclient.exceptions import NotEnoughAvailableBots, MaxActiveRounds

logger = logging.getLogger(__name__)


class Matches:
    # todo: have arena client check in with web service inorder to delay this
    @staticmethod
    def timeout_overtime_bot_games():
        with transaction.atomic():
            bots_in_matches = Bot.objects.select_for_update().filter(in_match=True,
                                                                     current_match__started__lt=timezone.now() - config.TIMEOUT_MATCHES_AFTER)
            for bot in bots_in_matches:
                logger.warning('bot {0} forcefully removed from match {1}'.format(bot.id, bot.current_match_id))
                bot.leave_match()

            matches_without_result = Match.objects.select_related('round').select_for_update().filter(
                started__lt=timezone.now() - config.TIMEOUT_MATCHES_AFTER, result__isnull=True)
            for match in matches_without_result:
                Result.objects.create(match=match, type='MatchCancelled', game_steps=0)
                if match.round is not None:  # if the match is part of a round, check for round completion
                    match.round.update_if_completed()

    @staticmethod
    def start_next_match(requesting_user):
        # todo: clean up this whole section

        Matches.timeout_overtime_bot_games()

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
                match = Match._locate_and_return_started_match(requesting_user)
                if match is None:
                    if Bot.objects.filter(active=True, in_match=False).count() < 2:
                        # All the active bots are already in a match
                        raise NotEnoughAvailableBots()
                    elif Round.max_active_rounds_reached():
                        raise MaxActiveRounds()
                    else:  # generate new round
                        Round.generate_new()
                        match = Match._locate_and_return_started_match(requesting_user)
                        if match is None:
                            cursor.execute("ROLLBACK")
                            raise Exception("Failed to start match for unknown reason.")
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
