import logging

from constance import config
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.db.models.signals import pre_save
from django.dispatch import receiver
from django.urls import reverse
from django.utils import timezone
from django.utils.functional import cached_property
from django.utils.html import escape
from django.utils.safestring import mark_safe
from django.utils.translation import gettext_lazy as _

from aiarena.core.models.mixins import LockableModelMixin

logger = logging.getLogger(__name__)


class User(AbstractUser, LockableModelMixin):
    PATREON_LEVELS = (
        ('none', 'None'),
        ('bronze', 'Bronze'),
        ('silver', 'Silver'),
        ('gold', 'Gold'),
        ('platinum', 'Platinum'),
        ('diamond', 'Diamond'),
    )
    USER_TYPES = (
        # When adding types here, ensure they are considered in post_save and validate_user_owner
        ('WEBSITE_USER', 'Website User'),
        ('ARENA_CLIENT', 'Arena Client'),
        ('SERVICE', 'Service'),
    )
    date_joined = models.DateTimeField(_('date joined'), default=timezone.now, blank=True)
    email = models.EmailField(unique=True)
    patreon_level = models.CharField(max_length=16, choices=PATREON_LEVELS, default='none', blank=True)
    type = models.CharField(max_length=16, choices=USER_TYPES, default='WEBSITE_USER', blank=True)
    extra_active_competition_participations = models.IntegerField(default=0, blank=True)
    extra_periodic_match_requests = models.IntegerField(default=0, blank=True)
    receive_email_comms = models.BooleanField(default=True, blank=True)
    sync_patreon_status = models.BooleanField(default=True, blank=True)

    # permissions
    can_request_games_for_another_authors_bot = models.BooleanField(default=False, blank=True)

    @cached_property
    def get_absolute_url(self):
        if self.type == 'WEBSITE_USER':
            return reverse('author', kwargs={'pk': self.pk})
        elif self.type == 'ARENA_CLIENT':
            return reverse('arenaclient', kwargs={'pk': self.pk})
        else:
            raise Exception("This user type does not have a url.")

    @cached_property
    def as_html_link(self):
        return mark_safe('<a href="{0}">{1}</a>'.format(self.get_absolute_url, escape(self.__str__())))

    BOTS_LIMIT_MAP = {
        "none": config.MAX_USER_BOT_PARTICIPATIONS_ACTIVE_FREE_TIER,
        "bronze": config.MAX_USER_BOT_PARTICIPATIONS_ACTIVE_BRONZE_TIER,
        "silver": config.MAX_USER_BOT_PARTICIPATIONS_ACTIVE_SILVER_TIER,
        "gold": config.MAX_USER_BOT_PARTICIPATIONS_ACTIVE_GOLD_TIER,
        "platinum": config.MAX_USER_BOT_PARTICIPATIONS_ACTIVE_PLATINUM_TIER,
        "diamond": config.MAX_USER_BOT_PARTICIPATIONS_ACTIVE_DIAMOND_TIER
    }

    def get_active_bots_limit(self):
        limit = self.BOTS_LIMIT_MAP[self.patreon_level]
        if limit is None:
            return None  # no limit
        else:
            return limit + self.extra_active_competition_participations

    def get_active_competition_participations_limit_display(self):
        limit = self.BOTS_LIMIT_MAP[self.patreon_level]
        if limit is None:
            return 'unlimited'  # no limit
        else:
            return limit + self.extra_active_competition_participations

    REQUESTED_MATCHES_LIMIT_MAP = {
        "none": config.MATCH_REQUEST_LIMIT_FREE_TIER,
        "bronze": config.MATCH_REQUEST_LIMIT_BRONZE_TIER,
        "silver": config.MATCH_REQUEST_LIMIT_SILVER_TIER,
        "gold": config.MATCH_REQUEST_LIMIT_GOLD_TIER,
        "platinum": config.MATCH_REQUEST_LIMIT_PLATINUM_TIER,
        "diamond": config.MATCH_REQUEST_LIMIT_DIAMOND_TIER,
    }

    @property
    def requested_matches_limit(self):
        return self.REQUESTED_MATCHES_LIMIT_MAP[self.patreon_level] + self.extra_periodic_match_requests

    @property
    def match_request_count_left(self):
        from .match import Match
        from .result import Result
        return self.requested_matches_limit \
               - Match.objects.only('id').filter(requested_by=self,
                                      created__gte=timezone.now() - config.REQUESTED_MATCHES_LIMIT_PERIOD).count() \
               + Result.objects.only('id').filter(submitted_by=self, type='MatchCancelled',
                                      created__gte=timezone.now() - config.REQUESTED_MATCHES_LIMIT_PERIOD).count()

    @property
    def has_donated(self):
        return self.patreon_level != 'none'

    @staticmethod
    def random_donator():
        # todo: apparently order_by('?') is really slow
        # https://stackoverflow.com/questions/962619/how-to-pull-a-random-record-using-djangos-orm#answer-962672
        return User.objects.only('id', 'username').exclude(patreon_level='none').order_by('?').first()

    @property
    def is_arenaclient(self):
        from .arena_client import ArenaClient  # avoid circular reference
        try:
            return (self.arenaclient is not None)
        except ArenaClient.DoesNotExist:
            return False

    @property
    def is_websiteuser(self):
        from .website_user import WebsiteUser  # avoid circular reference
        try:
            return (self.websiteuser is not None)
        except WebsiteUser.DoesNotExist:
            return False


@receiver(pre_save, sender=User)
def pre_save_user(sender, instance, **kwargs):
    if not instance.is_websiteuser:
        instance.set_unusable_password()
