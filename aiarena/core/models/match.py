import logging
from enum import Enum

from django.db import models, transaction
from django.db.models import F
from django.urls import reverse
from django.utils import timezone
from django.utils.html import escape
from django.utils.safestring import mark_safe

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

                from . import Season
                if self.round:  # if this is a ladder match, record the starting elo
                    for p in participations:
                        p.starting_elo = p.bot.seasonparticipation_set.get(season=Season.get_current_season()).elo
                        p.save()

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
    def create(round, map, bot1, bot2, requested_by=None):
        match = Match.objects.create(map=map, round=round, requested_by=requested_by)
        # create match participations
        from .match_participation import MatchParticipation  # avoid circular reference
        MatchParticipation.objects.create(match=match, participant_number=1, bot=bot1)
        MatchParticipation.objects.create(match=match, participant_number=2, bot=bot2)
        return match

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
        return mark_safe(f'<a href="{self.get_absolute_url()}">{escape(self.__str__())}</a>')
