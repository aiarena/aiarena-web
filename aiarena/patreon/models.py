import logging

from django.db import models
from django.utils import timezone

from constance import config

from aiarena.core.models import User
from aiarena.patreon.patreon import PatreonApi, PatreonOAuth, get_identity_paid_tier_title


logger = logging.getLogger(__name__)


class PatreonAccountBind(models.Model):
    DAYS_GRACE_PERIOD = 7
    """The number of days after the patreon subscription expires that the user will still be considered a patron.
    This is to account for the fact that the patreon API appears to randomly return 'none' for users that are still 
    patrons"""

    user = models.OneToOneField(User, on_delete=models.CASCADE, blank=True, null=True)
    access_token = models.CharField(max_length=64)
    refresh_token = models.CharField(max_length=64)
    last_token_refresh_attempt = models.DateTimeField(blank=True, null=True)
    """The datetime when the patreon token refresh was last attempted"""
    last_token_refresh_success = models.DateTimeField(blank=True, null=True)
    """The datetime when the patreon token refresh last succeeded"""
    last_token_refresh_failure = models.DateTimeField(blank=True, null=True)
    """The datetime when the patreon token refresh last failed"""
    last_token_refresh_failure_message = models.TextField(blank=True, null=True)
    """The exception text provided with the latest refresh failure"""
    patreon_user_id = models.CharField(max_length=64, blank=True, null=True)
    """The user id of the patreon user"""
    last_refresh_attempt_current_user_json = models.TextField(blank=True, null=True)
    """The JSON returned from Patreon's identity endpoint on the last refresh attempt."""
    last_had_pledge = models.DateTimeField(blank=True, null=True)
    """The datetime when the patreon API last return a pledge for this user.
    This is used in order to give a grace period before removing a user's patreon level."""

    def update_tokens(self):
        self.last_token_refresh_attempt = timezone.now()
        oauth_client = PatreonOAuth(config.PATREON_CLIENT_ID, config.PATREON_CLIENT_SECRET)
        try:
            self.access_token, self.refresh_token = oauth_client.update_tokens(self.refresh_token)
            self.last_token_refresh_success = timezone.now()
            self.save()
        except Exception as e:
            self.last_token_refresh_failure = timezone.now()
            self.last_token_refresh_failure_message = str(e)
            self.save()
            raise Exception(f"Failed to refresh patreon token for user {self.user.id}.") from e

    def update_user_patreon_tier(self):
        identity = PatreonApi(self.access_token).identity()
        logger.info(f"Refreshing patreon for user {self.user.id} {self.user.username}")
        self.last_refresh_attempt_current_user_json = str(identity)

        tier_title = get_identity_paid_tier_title(identity)
        if tier_title is not None:
            pledge = tier_title.lower()
            logger.info(f"Pledge found: {pledge}")
            self.user.patreon_level = pledge
            self.user.save()
            self.last_had_pledge = timezone.now()
        # If the user has an existing patreon level but no pledge,
        # then if we're past the grace period, remove the level.
        elif self.user.patreon_level != "none" and self._is_past_the_grace_period():
            logger.info("Pledge not found: setting to none")
            self.user.patreon_level = "none"
            self.user.save()

        self.patreon_user_id = identity["data"]["id"]
        self.save()
        logger.info(f"Patreon user id: {self.patreon_user_id}")

    def _is_past_the_grace_period(self):
        return self.last_had_pledge is None or (timezone.now() - self.last_had_pledge).days > self.DAYS_GRACE_PERIOD


class PatreonUnlinkedDiscordUID(models.Model):
    patreon_user_id = models.CharField(max_length=64, unique=True)
    discord_uid = models.CharField(max_length=64, unique=True)
