import json
import logging
import traceback
import urllib.parse

from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.sites.models import Site
from django.shortcuts import redirect
from django.urls import reverse
from django.views import View

from constance import config

from aiarena.patreon.models import PatreonAccountBind
from aiarena.patreon.patreon import PatreonOAuth


logger = logging.getLogger(__name__)


class PatreonBindView(LoginRequiredMixin, View):
    def get(self, request):
        site = Site.objects.get_current()
        domain = urllib.parse.quote_plus(site.domain)
        return redirect(
            "https://www.patreon.com/oauth2/authorize"
            "?response_type=code"
            "&scope=identity"
            "&client_id="
            + config.PATREON_CLIENT_ID
            + "&redirect_uri=https%3A%2F%2F"
            + domain
            + "%2Fpatreon%2Foauth%2Fredirect"
        )


class PatreonCallbackView(LoginRequiredMixin, View):
    """Completes the OAuth round trip, then returns to the SPA settings page,
    which re-fetches the new linked state.

    A failure is reported via `?link_error=patreon`, which the settings page
    turns into an error message. A user who cancelled on Patreon's consent
    screen (`error=access_denied`) did nothing wrong, so that isn't reported.
    """

    def get(self, request):
        if "error" in request.GET:
            return self.return_to_settings(request, failed=True)
        try:
            linked = self.link(request)
        except Exception:
            logger.error("Patreon linkage failed with error:\n" + traceback.format_exc())
            linked = False
        return self.return_to_settings(request, failed=not linked)

    @staticmethod
    def return_to_settings(request, *, failed: bool):
        url = reverse("dashboard_profile")
        if failed and request.GET.get("error") != "access_denied":
            url += "?" + urllib.parse.urlencode({"link_error": "patreon"})
        return redirect(url)

    @staticmethod
    def link(request) -> bool:
        oauth_client = PatreonOAuth(config.PATREON_CLIENT_ID, config.PATREON_CLIENT_SECRET)
        site = Site.objects.get_current()
        tokens = oauth_client.get_tokens(request.GET["code"], "https://" + site.domain + "/patreon/oauth/redirect")

        if "access_token" not in tokens or "refresh_token" not in tokens:
            logger.error("Patreon linkage failed. Tokens dump:\n" + json.dumps(tokens))
            return False

        account_bind, _ = PatreonAccountBind.objects.get_or_create(user=request.user)
        account_bind.access_token = tokens["access_token"]
        account_bind.refresh_token = tokens["refresh_token"]
        account_bind.save()

        try:
            account_bind.update_user_patreon_tier()
        except Exception:
            logger.error("Failed to update patreon tier with error:\n" + traceback.format_exc())
        return True
