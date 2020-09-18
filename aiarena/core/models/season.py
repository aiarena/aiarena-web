import io
import logging

from django.core.files import File
from django.db import models, transaction
from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from django.urls import reverse
from django.utils import timezone
from django.utils.html import escape
from django.utils.safestring import mark_safe

from aiarena.api.arenaclient.exceptions import NoCurrentSeason, MultipleCurrentSeasons
from .mixins import LockableModelMixin


logger = logging.getLogger(__name__)


def replay_archive_upload_to(instance, filename):
    return '/'.join(['replays', 'season_' + str(instance.number) + '_zip'])

class Season(models.Model, LockableModelMixin):
    """ Represents a season of play in the context of a ladder """
    SEASON_STATUSES = (
        ('created', 'Created'),  # The initial state for a season. Functionally identical to paused.
        ('paused', 'Paused'),  # While a season is paused, existing rounds can be played, but no new ones are generated.
        ('open', 'Open'),  # When a season is open, new rounds can be generated and played.
        ('closing', 'Closing'),
        # When a season is closing, it's the same as paused except it will automatically move to closed when all rounds are finished.
        ('closed', 'Closed'),  # Functionally identical to paused, except not intended to change after this status.
    )
    number = models.IntegerField(blank=True, editable=False)
    date_created = models.DateTimeField(auto_now_add=True)
    date_opened = models.DateTimeField(blank=True, null=True)
    date_closed = models.DateTimeField(blank=True, null=True)
    status = models.CharField(max_length=16, choices=SEASON_STATUSES, default='created')
    previous_season_files_cleaned = models.BooleanField(default=False)

    def __str__(self):
        return self.name

    @property
    def name(self):
        return 'Season ' + str(self.number)

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
            return "Cannot pause a season with a status of {}".format(self.status)

    @transaction.atomic
    def open(self):
        from .bot import Bot
        self.lock_me()

        if not self.previous_season_files_cleaned:
            return "Cannot open a season where previous_season_replays_cleaned has not been marked as True."

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
            return "Cannot open a season with a status of {}".format(self.status)

    @transaction.atomic
    def start_closing(self):
        self.lock_me()
        if self.is_open or self.is_paused:
            self.status = 'closing'
            self.save()
            return None
        else:
            return "Cannot start closing a season with a status of {}".format(self.status)

    def try_to_close(self):
        from .round import Round
        from .bot import Bot
        if self.is_closing and Round.objects.filter(season=self, complete=False).count() == 0:
            with transaction.atomic():
                self.__class__.objects.select_for_update().get(id=self.id)
                self.status = 'closed'
                self.date_closed = timezone.now()
                self.save()

                # deactivate all bots
                for bot in Bot.objects.all():
                    bot.active = False
                    bot.save()
                # todo: sanity check replay archive contents against results.
                # todo: then dump results data as JSON?
                # todo: then wipe all replay/log files?

    @staticmethod
    def get_current_season(select_for_update: bool = False) -> 'Season':
        try:
            #  will fail if there is more than 1 current season or 0 current seasons
            return Season.objects.select_for_update().get(date_closed__isnull=True) \
                if select_for_update else Season.objects.get(date_closed__isnull=True)
        except Season.DoesNotExist:
            raise NoCurrentSeason()  # todo: separate between core and API exceptions
        except Season.MultipleObjectsReturned:
            raise MultipleCurrentSeasons()  # todo: separate between core and API exceptions

    def get_absolute_url(self):
        return reverse('season', kwargs={'pk': self.pk})

    def as_html_link(self):
        return mark_safe(f'<a href="{self.get_absolute_url()}">{escape(self.__str__())}</a>')

    @staticmethod
    def get_current_season_or_none():
        try:
            return Season.get_current_season()
        except NoCurrentSeason:
            return None
        except MultipleCurrentSeasons:
            return None

    def get_absolute_url(self):
        return reverse('season', kwargs={'pk': self.pk})

    def as_html_link(self):
        return mark_safe(f'<a href="{self.get_absolute_url()}">{escape(self.__str__())}</a>')


@receiver(pre_save, sender=Season)
def pre_save_season(sender, instance, **kwargs):
    if instance.number is None:
        instance.number = Season.objects.all().count() + 1  # todo: redo this for multiladders

