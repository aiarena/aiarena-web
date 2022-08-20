import json
import logging

import requests
from constance import config


logger = logging.getLogger(__name__)


# Reimplementation of: https://github.com/Patreon/patreon-python/


class PatreonOAuth:
    def __init__(self, client_id, client_secret):
        self.client_id = client_id
        self.client_secret = client_secret

    def get_tokens(self, code, redirect_uri):
        return self.__update_token({
            "code": code,
            "grant_type": "authorization_code",
            "client_id": self.client_id,
            "client_secret": self.client_secret,
            "redirect_uri": redirect_uri
        })

    def refresh_token(self, refresh_token):
        return self.__update_token({
            "grant_type": "refresh_token",
            "refresh_token": refresh_token,
            "client_id": self.client_id,
            "client_secret": self.client_secret
        })

    @staticmethod
    def __update_token(params):
        response = requests.post(
            "https://www.patreon.com/api/oauth2/token",
            params=params,
            headers={
                'Content-type': 'application/x-www-form-urlencoded',
                'User-Agent': user_agent_string(),
            }
        )
        return response.json()

    def update_tokens(self, refresh_token) -> (str, str):
        oauth_client = PatreonOAuth(self.client_id, self.client_secret)
        tokens = oauth_client.refresh_token(refresh_token)
        if 'access_token' in tokens and 'refresh_token' in tokens:
            return tokens['access_token'], tokens['refresh_token']
        else:
            raise Exception("Failed to refresh patreon token. Tokens dump:\n" + json.dumps(tokens))


def user_agent_string():
    return 'Python'


class PatreonApi:
    def __init__(self, token):
        self.token = token

    def current_user(self):
        return self.get_from_oauth_endpoint('current_user')

    def current_user_campaigns(self):
        return self.get_from_oauth_endpoint('current_user/campaigns')

    def campaign_pledges(self, campaign_id):
        return self.get_from_oauth_endpoint(f'campaigns/{campaign_id}/pledges')

    def user(self, user_id):
        return self.get_from_endpoint(f'user/{user_id}')

    def get_from_oauth_endpoint(self, endpoint):
        return self.get_from_endpoint(f'oauth2/api/{endpoint}')

    def get_from_endpoint(self, endpoint):
        response = requests.get(
            "https://www.patreon.com/api/{}".format(endpoint),
            headers={
                'Authorization': "Bearer {}".format(self.token),
                'User-Agent': user_agent_string(),
            }
        )
        return response.json()


def update_unlinked_discord_users():
    if config.PATREON_CLIENT_ID and config.PATREON_CLIENT_SECRET:
        # avoid circular import
        from aiarena.patreon.models import PatreonUnlinkedDiscordUID, PatreonAccountBind

        access_token, _ = refresh_creator_tokens()
        api = PatreonApi(access_token)
        campaigns = api.current_user_campaigns()
        campaign_id = get_campaign_id(campaigns)
        campaign = api.campaign_pledges(campaign_id)
        discord_uids = get_pledge_user_discord_uids(campaign)

        PatreonUnlinkedDiscordUID.objects.all().delete()

        for discord_uid in discord_uids:
            if not PatreonAccountBind.objects.filter(patreon_user_id=discord_uid['patreon_user_id']).exists():
                PatreonUnlinkedDiscordUID.objects.create(patreon_user_id=discord_uid['patreon_user_id'],
                                                         discord_uid=discord_uid['discord_uid'])


def refresh_creator_tokens() -> (str, str):
    oauth_client = PatreonOAuth(config.PATREON_CLIENT_ID, config.PATREON_CLIENT_SECRET)
    try:
        access_token, refresh_token = oauth_client.update_tokens(config.PATREON_CREATOR_REFRESH_TOKEN)
        config.PATREON_CREATOR_REFRESH_TOKEN = refresh_token
        return access_token, refresh_token
    except Exception as e:
        raise Exception(f"Failed to refresh Patreon creator tokens.") from e


def get_campaign_id(campaigns) -> str:
    if 'data' in campaigns and len(campaigns['data']) == 1 and 'id' in campaigns['data'][0]:
        return campaigns['data'][0]['id']
    raise Exception('Unable to locate campaign.')


def get_pledge_user_discord_uids(campaign):
    if 'included' in campaign:
        discord_uids = []
        for entry in campaign['included']:
            if entry['type'] == 'user':
                discord = entry['attributes']['social_connections']['discord']
                if discord is not None:
                    if 'user_id' in discord:
                        discord_uids.append({'patreon_user_id': entry['id'], 'discord_uid': discord['user_id']})
                    else:
                        raise Exception('Discord user_id was missing!')
        return discord_uids
    raise Exception('Unable to locate pledge user discord uids.')
