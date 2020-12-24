import logging

from django.db import models, transaction
from django.urls import reverse
from django.utils import timezone
from django.utils.html import escape
from django.utils.safestring import mark_safe

from .game_type import GameMode
from .mixins import LockableModelMixin

logger = logging.getLogger(__name__)


class CompetitionType(models.TextChoices):
    LEAGUE = u'L', 'League - Round Robin'
    # TOURNAMENT = u'T', 'Tournament'
    # CUSTOM = u'C', 'Custom'
    # flash_challenge = u'F', 'FlashChallenge'


class Competition(models.Model, LockableModelMixin):
    """ Represents a competition of play in the context of a ladder """
    COMPETITION_STATUSES = (
        ('created', 'Created'),  # The initial state for a competition. Functionally identical to paused.
        ('paused', 'Paused'),  # While a competition is paused, existing rounds can be played, but no new ones are generated.
        ('open', 'Open'),  # When a competition is open, new rounds can be generated and played.
        ('closing', 'Closing'),
        # When a competition is closing, it's the same as paused except it will automatically move to closed when all rounds are finished.
        ('closed', 'Closed'),  # Functionally identical to paused, except not intended to change after this status.
    )
    # name = models.CharField(max_length=50, unique=True)
    name = models.CharField(max_length=50, null=True)
    type = models.CharField(max_length=32,
                            choices=CompetitionType.choices,
                            default=CompetitionType.LEAGUE)
    game_mode = models.ForeignKey(GameMode, on_delete=models.CASCADE, related_name='game_modes')
    date_created = models.DateTimeField(auto_now_add=True, blank=True)
    date_opened = models.DateTimeField(blank=True, null=True)
    date_closed = models.DateTimeField(blank=True, null=True)
    status = models.CharField(max_length=16, choices=COMPETITION_STATUSES, default='created', blank=True)

    def __str__(self):
        return self.name

    @property
    def is_paused(self):
        return self.status in ['paused', 'created']

    @property
    def is_open(self):
        return self.status == 'open'

    @property
    def is_closing(self):
        return self.status == 'closing'

    @transaction.atomic
    def pause(self):
        self.lock_me()
        if self.status == 'open':
            self.status = 'paused'
            self.save()
            return None
        else:
            return "Cannot pause a competition with a status of {}".format(self.status)

    @transaction.atomic
    def open(self):
        from .bot import Bot
        self.lock_me()

        if self.status in ['created', 'paused']:
            if self.status == 'created':
                self.date_opened = timezone.now()

                # double check bots aren't active and if so deactivate them
                for bot in Bot.objects.all():
                    if bot.active:
                        bot.active = False
                    bot.save()

            self.status = 'open'
            self.save()
            return None
        else:
            return "Cannot open a competition with a status of {}".format(self.status)

    @transaction.atomic
    def start_closing(self):
        self.lock_me()
        if self.is_open or self.is_paused:
            self.status = 'closing'
            self.save()
            return None
        else:
            return "Cannot start closing a competition with a status of {}".format(self.status)

    @transaction.atomic
    def try_to_close(self):
        from .round import Round
        from .bot import Bot
        if self.is_closing and Round.objects.filter(competition=self, complete=False).count() == 0 and \
                Competition.objects.filter(id=self.id, status='closing') \
                .update(status='closed', date_closed=timezone.now()) > 0:
            # deactivate all bots
            for bot in Bot.objects.all():
                bot.active = False
                bot.save()
            # todo: sanity check replay archive contents against results.
            # todo: then dump results data as JSON?
            # todo: then wipe all replay/log files?

    def get_absolute_url(self):
        return reverse('competition', kwargs={'pk': self.pk})

    def as_html_link(self):
        return mark_safe(f'<a href="{self.get_absolute_url()}">{escape(self.__str__())}</a>')

    def get_absolute_url(self):
        return reverse('competition', kwargs={'pk': self.pk})

    def as_html_link(self):
        return mark_safe(f'<a href="{self.get_absolute_url()}">{escape(self.__str__())}</a>')

