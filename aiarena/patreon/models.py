from django.utils import timezone
import json
import logging

from constance import config

from aiarena.core.models import User
from aiarena.patreon.patreon import PatreonOAuth, PatreonApi

logger = logging.getLogger(__name__)

from django.db import models


class PatreonAccountBind(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, blank=True, null=True)
    access_token = models.CharField(max_length=64)
    refresh_token = models.CharField(max_length=64)
    last_token_refresh_success = models.DateTimeField(blank=True, null=True)
    """The datetime when the patreon token refresh last succeeded"""

    def update_refresh_token(self):
        oauth_client = PatreonOAuth(config.PATREON_CLIENT_ID, config.PATREON_CLIENT_SECRET)
        tokens = oauth_client.refresh_token(self.refresh_token)
        if 'access_token' in tokens and 'refresh_token' in tokens:
            self.access_token = tokens['access_token']
            self.refresh_token = tokens['refresh_token']
            self.last_token_refresh_success = timezone.now()
            self.save()
        else:
            raise Exception(f"Failed to refresh patreon token for user {self.user.id}. Tokens dump:\n" + json.dumps(tokens))

    def update_user_patreon_tier(self):
        api_client = PatreonApi(self.access_token)
        user = api_client.current_user()
        patreon_level = 'none'
        if self.has_pledge(user):
            patreon_level = self.get_pledge_reward_name(user, self.get_pledge_reward_id(user)).lower()

        self.user.patreon_level = patreon_level
        self.user.save()

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

    def get_pledge_reward_name(self, user, id: str) -> str:
        for entry in user['included']:
            if entry['type'] == 'reward' and entry['id'] == id:
                return entry['attributes']['title']
        raise Exception('Unable to locate reward.')


