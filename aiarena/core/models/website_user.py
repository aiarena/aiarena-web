import logging

from django.db import models
from django.utils import timezone

from constance import config

from .user import User
from ..services.supporter_benefits import SupporterBenefits

logger = logging.getLogger(__name__)


class WebsiteUser(User):
    """Represents a website user/bot author"""

    single_use_match_requests = models.IntegerField(default=0, blank=True)
    """UNUSED AS OF YET"""
    """Single-use match requests that go on top of any periodic match requests a user might have.
    Periodic match requests are used first before these."""

    @property
    def requested_matches_limit(self):
        # TODO: This is a duplicate of the method in User. Refactor to use the same method.
        return SupporterBenefits.get_requested_matches_limit(self)

    @property
    def match_request_count_left(self):
        # TODO: This is a duplicate of the method in User. Refactor to use the same method.
        from .match import Match
        from .result import Result

        return (
            self.requested_matches_limit
            - Match.objects.only("id")
            .filter(requested_by=self, created__gte=timezone.now() - config.REQUESTED_MATCHES_LIMIT_PERIOD)
            .count()
            + Result.objects.only("id")
            .filter(
                submitted_by=self,
                type="MatchCancelled",
                created__gte=timezone.now() - config.REQUESTED_MATCHES_LIMIT_PERIOD,
            )
            .count()
        )

    class Meta:
        verbose_name = "WebsiteUser"
