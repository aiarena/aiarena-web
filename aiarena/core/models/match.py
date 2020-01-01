import logging
from enum import Enum

from django.db import models, transaction, connection
from django.db.models import F
from django.urls import reverse
from django.utils import timezone
from django.utils.html import escape
from wiki.models import Article

from aiarena.api.arenaclient.exceptions import NotEnoughAvailableBots, MaxActiveRounds
from aiarena.core.exceptions import BotNotInMatchException
from .map import Map
from .round import Round
from .user import User

logger = logging.getLogger(__name__)


# todo: structure for separate ladder types
class Match(models.Model):
    """ Represents a match between 2 bots. Usually this is within the context of a round, but doesn't have to be. """
    map = models.ForeignKey(Map, on_delete=models.PROTECT)
    created = models.DateTimeField(auto_now_add=True)
    started = models.DateTimeField(blank=True, null=True, editable=False)
    assigned_to = models.ForeignKey(User, on_delete=models.PROTECT, blank=True, null=True,
                                    related_name='assigned_matches')
    round = models.ForeignKey(Round, on_delete=models.CASCADE, blank=True, null=True)
    requested_by = models.ForeignKey(User, on_delete=models.SET_NULL, blank=True, null=True,
                                     related_name='requested_matches')

    def __str__(self):
        return self.id.__str__()

    class StartResult(Enum):
        SUCCESS = 1
        BOT_ALREADY_IN_MATCH = 2
        FAIL_ALREADY_STARTED = 3

    def start(self, assign_to):
        with transaction.atomic():
            Match.objects.select_for_update().get(id=self.id)  # lock self to avoid race conditions
            if self.started is None:
                # is a bot currently in a match?
                from .match_participation import MatchParticipation  # avoid circular reference
                participations = MatchParticipation.objects.select_for_update().filter(match=self)
                for p in participations:
                    if p.bot.in_match:
                        return Match.StartResult.BOT_ALREADY_IN_MATCH

                for p in participations:
                    p.bot.enter_match(self)

                self.started = timezone.now()
                self.assigned_to = assign_to
                self.save()
                return Match.StartResult.SUCCESS
            else:
                return Match.StartResult.FAIL_ALREADY_STARTED

    @property
    def participant1(self):
        return self.matchparticipation_set.get(participant_number=1)

    @property
    def participant2(self):
        return self.matchparticipation_set.get(participant_number=2)

    @property
    def is_requested(self):
        return self.requested_by is not None

    @staticmethod
    def start_next_match(requesting_user):

        from . import Bot, Season

        # todo: clean up this whole section

        Bot.timeout_overtime_bot_games()

        with connection.cursor() as cursor:
            # Lock the matches table
            # this needs to happen so that if we end up having to generate a new set of matches
            # then we don't hit a race condition
            # MySql also requires we lock any other tables we access as well.
            from .match_participation import MatchParticipation  # avoid circular reference
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

    @staticmethod
    def create(round, map, bot1, bot2, requested_by=None):
        match = Match.objects.create(map=map, round=round, requested_by=requested_by)
        # create match participations
        from .match_participation import MatchParticipation  # avoid circular reference
        MatchParticipation.objects.create(match=match, participant_number=1, bot=bot1)
        MatchParticipation.objects.create(match=match, participant_number=2, bot=bot2)
        return match

    # todo: let us specify the map
    @staticmethod
    def request_bot_match(bot, opponent=None, map=None, user=None):
        # if opponent is none a random one gets chosen
        return Match.create(None, map if map is not None else Map.random_active(), bot,
                            opponent if opponent is not None else bot.get_random_available_excluding_self(),
                            user)

    class CancelResult(Enum):
        SUCCESS = 1
        MATCH_DOES_NOT_EXIST = 3
        RESULT_ALREADY_EXISTS = 2

    def cancel(self, requesting_user):
        from . import Result
        with transaction.atomic():
            try:
                # do this to lock the record
                # select_related() for the round data
                match = Match.objects.select_related('round').select_for_update().get(pk=self.id)
            except Match.DoesNotExist:
                return Match.CancelResult.MATCH_DOES_NOT_EXIST  # should basically not happen, but just in case

            if Result.objects.filter(match=match).count() > 0:
                return Match.CancelResult.RESULT_ALREADY_EXISTS

            Result.objects.create(match=match, type='MatchCancelled', game_steps=0, submitted_by=requesting_user)

            # attempt to kick the bots from the match
            if match.started:
                try:
                    bot1 = match.matchparticipation_set.select_related().select_for_update().get(
                        participant_number=1).bot
                    bot1.leave_match(match.id)
                except BotNotInMatchException:
                    pass
                try:
                    bot2 = match.matchparticipation_set.select_related().select_for_update().get(
                        participant_number=2).bot
                    bot2.leave_match(match.id)
                except BotNotInMatchException:
                    pass
            else:
                match.started = timezone.now()
                match.save()

            if match.round is not None:
                match.round.update_if_completed()

    @classmethod
    def _locate_and_return_started_match(cls, requesting_user):
        # todo: apparently order_by('?') is really slow
        # https://stackoverflow.com/questions/962619/how-to-pull-a-random-record-using-djangos-orm#answer-962672
        # Wrapping the model call here in list() fixes the ordering not being applied.
        # Probably due to Django's lazy evaluation - it forces evaluation thus ensuring the order by is processed
        for match in list(
                Match.objects.filter(started__isnull=True).order_by(F('round_id').asc(nulls_last=False), '?')):
            if match.start(requesting_user) == Match.StartResult.SUCCESS:
                return match
        return None

    def get_absolute_url(self):
        return reverse('match', kwargs={'pk': self.pk})

    def as_html_link(self):
        return '<a href="{0}">{1}</a>'.format(self.get_absolute_url(), escape(self.__str__()))
