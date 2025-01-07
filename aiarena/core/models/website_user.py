import logging

from django.db import models

from .user import User


logger = logging.getLogger(__name__)


class WebsiteUser(User):
    """Represents a website user/bot author"""

    single_use_match_requests = models.IntegerField(default=0, blank=True)
    """UNUSED AS OF YET"""
    """Single-use match requests that go on top of any periodic match requests a user might have.
    Periodic match requests are used first before these."""

    class Meta:
        verbose_name = "WebsiteUser"
