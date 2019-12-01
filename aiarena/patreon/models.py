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

    def refresh_token(self):
        oauth_client = PatreonOAuth(config.PATREON_CLIENT_ID, config.PATREON_CLIENT_SECRET)
        tokens = oauth_client.refresh_token(self.refresh_token)
        if 'access_token' in tokens and 'refresh_token' in tokens:
            self.access_token = tokens['access_token']
            self.refresh_token = tokens['refresh_token']
            self.save()
        else:
            raise Exception("Failed to refresh patreon token.")

    def update_user_patreon_tier(self):
        api_client = PatreonApi(self.access_token)
        user = api_client.current_user()
        patreon_level = 'none'
        if 'included' in user:
            for entry in user['included']:
                if entry['type'] == 'pledge':
                    if entry['attributes']['amount_cents'] >= 10000:  # diamond
                        patreon_level = 'diamond'
                        break
                    elif entry['attributes']['amount_cents'] >= 5000:  # platinum
                        patreon_level = 'platinum'
                        break
                    elif entry['attributes']['amount_cents'] >= 2500:  # gold
                        patreon_level = 'gold'
                        break
                    elif entry['attributes']['amount_cents'] >= 1000:  # silver
                        patreon_level = 'silver'
                        break
                    elif entry['attributes']['amount_cents'] >= 500:  # bronze
                        patreon_level = 'bronze'
                        break
                    else:
                        patreon_level = 'none'
                        break

        self.user.patreon_level = patreon_level
        self.user.save()


