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
        return self.__update_token(
            {
                "code": code,
                "grant_type": "authorization_code",
                "client_id": self.client_id,
                "client_secret": self.client_secret,
                "redirect_uri": redirect_uri,
            }
        )

    def refresh_token(self, refresh_token):
        return self.__update_token(
            {
                "grant_type": "refresh_token",
                "refresh_token": refresh_token,
                "client_id": self.client_id,
                "client_secret": self.client_secret,
            }
        )

    @staticmethod
    def __update_token(params):
        response = requests.post(
            "https://www.patreon.com/api/oauth2/token",
            params=params,
            headers={
                "Content-type": "application/x-www-form-urlencoded",
                "User-Agent": user_agent_string(),
            },
        )
        return response.json()

    def update_tokens(self, refresh_token) -> (str, str):
        oauth_client = PatreonOAuth(self.client_id, self.client_secret)
        tokens = oauth_client.refresh_token(refresh_token)
        if "access_token" in tokens and "refresh_token" in tokens:
            return tokens["access_token"], tokens["refresh_token"]
        else:
            raise Exception("Failed to refresh patreon token. Tokens dump:\n" + json.dumps(tokens))


def user_agent_string():
    return "AI Arena - Website"


class PatreonApi:
    MEMBERS_PAGE_SIZE = 500

    def __init__(self, token):
        self.token = token

    def identity(self):
        """The token's user, along with their membership to our campaign and the tiers it entitles them to."""
        return self.get_from_endpoint(
            "identity",
            {
                "include": "memberships.currently_entitled_tiers",
                "fields[tier]": "title,amount_cents",
            },
        )

    def campaigns(self):
        return self.get_from_endpoint("campaigns")

    def campaign_members(self, campaign_id):
        """Yields each page of the campaign's members, along with their users and entitled tiers."""
        params = {
            "include": "currently_entitled_tiers,user",
            "fields[tier]": "title,amount_cents",
            "fields[user]": "social_connections",
            "page[count]": self.MEMBERS_PAGE_SIZE,
        }
        while True:
            page = self.get_from_endpoint(f"campaigns/{campaign_id}/members", params)
            yield page
            cursors = page.get("meta", {}).get("pagination", {}).get("cursors") or {}
            if not cursors.get("next"):
                return
            params["page[cursor]"] = cursors["next"]

    def get_from_endpoint(self, endpoint, params=None):
        response = requests.get(
            f"https://www.patreon.com/api/oauth2/v2/{endpoint}",
            params=params,
            headers={
                "Authorization": f"Bearer {self.token}",
                "User-Agent": user_agent_string(),
            },
        )
        # An error response must never be mistaken for a patron without a pledge.
        response.raise_for_status()
        return response.json()


def update_unlinked_discord_users():
    if config.PATREON_CLIENT_ID and config.PATREON_CLIENT_SECRET and config.PATREON_CREATOR_REFRESH_TOKEN:
        # avoid circular import
        from aiarena.patreon.models import PatreonAccountBind, PatreonUnlinkedDiscordUID

        access_token, _ = refresh_creator_tokens()
        api = PatreonApi(access_token)
        campaign_id = get_campaign_id(api.campaigns())
        discord_uids = [
            discord_uid
            for members_page in api.campaign_members(campaign_id)
            for discord_uid in get_patron_discord_uids(members_page)
        ]

        PatreonUnlinkedDiscordUID.objects.all().delete()

        for discord_uid in discord_uids:
            if not PatreonAccountBind.objects.filter(patreon_user_id=discord_uid["patreon_user_id"]).exists():
                PatreonUnlinkedDiscordUID.objects.create(
                    patreon_user_id=discord_uid["patreon_user_id"], discord_uid=discord_uid["discord_uid"]
                )


def refresh_creator_tokens() -> (str, str):
    oauth_client = PatreonOAuth(config.PATREON_CLIENT_ID, config.PATREON_CLIENT_SECRET)
    try:
        access_token, refresh_token = oauth_client.update_tokens(config.PATREON_CREATOR_REFRESH_TOKEN)
        config.PATREON_CREATOR_REFRESH_TOKEN = refresh_token
        return access_token, refresh_token
    except Exception as e:
        raise Exception("Failed to refresh Patreon creator tokens.") from e


def get_campaign_id(campaigns) -> str:
    if "data" in campaigns and len(campaigns["data"]) == 1 and "id" in campaigns["data"][0]:
        return campaigns["data"][0]["id"]
    raise Exception("Unable to locate campaign.")


def _included_resources(document) -> dict:
    return {(entry["type"], entry["id"]): entry for entry in document.get("included", [])}


def _paid_tier_title(member, included) -> str | None:
    """
    The title of the highest paid tier the member is currently entitled to, or None if there isn't one.
    Free members hold a membership too, so being a member doesn't by itself make someone a patron.
    """
    tiers = [included[(ref["type"], ref["id"])] for ref in member["relationships"]["currently_entitled_tiers"]["data"]]
    paid_tiers = [tier for tier in tiers if tier["attributes"]["amount_cents"] > 0]
    if not paid_tiers:
        return None
    return max(paid_tiers, key=lambda tier: tier["attributes"]["amount_cents"])["attributes"]["title"]


def get_identity_paid_tier_title(identity) -> str | None:
    """The title of the paid tier the identity's user is currently entitled to, or None if they aren't a patron."""
    included = _included_resources(identity)
    for entry in included.values():
        if entry["type"] == "member":
            title = _paid_tier_title(entry, included)
            if title is not None:
                return title
    return None


def get_patron_discord_uids(members_page):
    included = _included_resources(members_page)
    discord_uids = []
    for member in members_page["data"]:
        if _paid_tier_title(member, included) is None:
            continue
        user = included[("user", member["relationships"]["user"]["data"]["id"])]
        discord = (user["attributes"].get("social_connections") or {}).get("discord")
        if discord is not None:
            if "user_id" in discord:
                discord_uids.append({"patreon_user_id": user["id"], "discord_uid": discord["user_id"]})
            else:
                raise Exception("Discord user_id was missing!")
    return discord_uids
