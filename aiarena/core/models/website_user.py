import logging

from constance import config
from django.db import models
from django.utils import timezone

from .user import User

logger = logging.getLogger(__name__)


class WebsiteUser(User):
    """Represents a website user/bot author"""
    single_use_match_requests = models.IntegerField(default=0, blank=True)
    """UNUSED AS OF YET"""
    """Single-use match requests that go on top of any periodic match requests a user might have.
    Periodic match requests are used first before these."""

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


    class Meta:
        verbose_name = 'WebsiteUser'
