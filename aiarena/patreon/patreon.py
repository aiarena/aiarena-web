import logging

import requests

logger = logging.getLogger(__name__)

# Reimplementation of: https://github.com/Patreon/patreon-python/


class PatreonOAuth:
    def __init__(self, client_id, client_secret):
        self.client_id = client_id
        self.client_secret = client_secret

    def get_tokens(self, code, redirect_uri):
        logger.error("get_tokens")
        return self.__update_token({
            "code": code,
            "grant_type": "authorization_code",
            "client_id": self.client_id,
            "client_secret": self.client_secret,
            "redirect_uri": redirect_uri
        })

    def refresh_token(self, refresh_token):
        logger.error("refresh_token")
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
        logger.error("response.status_code: " + str(response.status_code))
        return response.json()


def user_agent_string():
    return 'Python'


class PatreonApi:
    def __init__(self, token):
        self.token = token

    def current_user(self):
        return self.get_from_endpoint('current_user')

    def get_from_endpoint(self, endpoint):
        response = requests.get(
            "https://www.patreon.com/api/oauth2/api/{}".format(endpoint),
            headers={
                'Authorization': "Bearer {}".format(self.token),
                'User-Agent': user_agent_string(),
            }
        )
        return response.json()
