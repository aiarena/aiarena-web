import logging

from constance import config
from django.utils import timezone

from aiarena.core.models import User
from aiarena.patreon.patreon import PatreonOAuth, PatreonApi

logger = logging.getLogger(__name__)

from django.db import models


class PatreonAccountBind(models.Model):
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

    def update_tokens(self):
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
        api_client = PatreonApi(self.access_token)
        user = api_client.current_user()
        patreon_level = 'none'
        if self.has_pledge(user):
            patreon_level = self.get_pledge_reward_name(user, self.get_pledge_reward_id(user)).lower()

        self.user.patreon_level = patreon_level
        self.user.save()

        self.patreon_user_id = self.get_patreon_user_id(user)
        self.save()

    def has_pledge(self, user) -> bool:
        if 'included' in user:
            for entry in user['included']:
                if entry['type'] == 'pledge':
                    return True
        return False

    def get_pledge_reward_id(self, user) -> str:
        for entry in user['included']:
            if entry['type'] == 'pledge':
                return entry['relationships']['reward']['data']['id']
        raise Exception('Unable to locate reward for pledge.')

    def get_patreon_user_id(self, user) -> str:
        if 'data' in user and 'id' in user['data']:
            return user['data']['id']
        return None

    def get_pledge_reward_name(self, user, id: str) -> str:
        for entry in user['included']:
            if entry['type'] == 'reward' and entry['id'] == id:
                return entry['attributes']['title']
        raise Exception('Unable to locate reward.')


class PatreonUnlinkedDiscordUID(models.Model):
    patreon_user_id = models.CharField(max_length=64, unique=True)
    discord_uid = models.CharField(max_length=64, unique=True)
