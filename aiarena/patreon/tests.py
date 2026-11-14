from unittest import mock

from django.test import SimpleTestCase
from django.urls import reverse

import pytest

from aiarena.patreon.models import PatreonAccountBind
from aiarena.patreon.patreon import get_identity_paid_tier_title, get_patron_discord_uids


def tier(tier_id, title, amount_cents):
    return {"type": "tier", "id": tier_id, "attributes": {"title": title, "amount_cents": amount_cents}}


def member(member_id, tier_ids, user_id=None):
    relationships = {"currently_entitled_tiers": {"data": [{"type": "tier", "id": tier_id} for tier_id in tier_ids]}}
    if user_id is not None:
        relationships["user"] = {"data": {"type": "user", "id": user_id}}
    return {"type": "member", "id": member_id, "relationships": relationships}


def user(user_id, social_connections):
    return {"type": "user", "id": user_id, "attributes": {"social_connections": social_connections}}


def identity(included):
    return {"data": {"type": "user", "id": "1"}, "included": included}


class IdentityPaidTierTitleTests(SimpleTestCase):
    def test_not_a_member(self):
        self.assertIsNone(get_identity_paid_tier_title({"data": {"type": "user", "id": "1"}}))

    def test_member_without_entitled_tiers(self):
        self.assertIsNone(get_identity_paid_tier_title(identity([member("m1", [])])))

    def test_free_member(self):
        document = identity([member("m1", ["t0"]), tier("t0", "Free", 0)])
        self.assertIsNone(get_identity_paid_tier_title(document))

    def test_paid_member(self):
        document = identity([member("m1", ["t0", "t2"]), tier("t0", "Free", 0), tier("t2", "Gold", 1000)])
        self.assertEqual(get_identity_paid_tier_title(document), "Gold")

    def test_highest_paid_tier_wins(self):
        document = identity([member("m1", ["t1", "t2"]), tier("t1", "Bronze", 100), tier("t2", "Gold", 1000)])
        self.assertEqual(get_identity_paid_tier_title(document), "Gold")


class PatronDiscordUidsTests(SimpleTestCase):
    def test_only_patrons_with_discord_are_returned(self):
        members_page = {
            "data": [
                member("m1", ["t1"], user_id="u1"),
                member("m2", ["t0"], user_id="u2"),
                member("m3", [], user_id="u3"),
                member("m4", ["t1"], user_id="u4"),
                member("m5", ["t1"], user_id="u5"),
            ],
            "included": [
                tier("t0", "Free", 0),
                tier("t1", "Bronze", 100),
                user("u1", {"discord": {"user_id": "d1"}}),
                user("u2", {"discord": {"user_id": "d2"}}),
                user("u3", {"discord": {"user_id": "d3"}}),
                user("u4", {"discord": None}),
                user("u5", None),
            ],
        }
        self.assertEqual(get_patron_discord_uids(members_page), [{"patreon_user_id": "u1", "discord_uid": "d1"}])


class TestPatreonCallback:
    """The OAuth callback links the account and lands back on the SPA settings page."""

    @staticmethod
    def call(client, tokens, params=None):
        with mock.patch("aiarena.patreon.views.PatreonOAuth.get_tokens", return_value=tokens):
            return client.get(reverse("patreon_oauth_redirect"), params or {"code": "abc"})

    def test_success_links_and_redirects_to_dashboard(self, client, user):
        client.force_login(user)
        with mock.patch.object(PatreonAccountBind, "update_user_patreon_tier"):
            response = self.call(client, {"access_token": "a", "refresh_token": "r"})

        assert response.status_code == 302
        assert response.url == reverse("dashboard_profile")
        bind = PatreonAccountBind.objects.get(user=user)
        assert (bind.access_token, bind.refresh_token) == ("a", "r")

    def test_tier_update_failure_still_links(self, client, user):
        client.force_login(user)
        with mock.patch.object(PatreonAccountBind, "update_user_patreon_tier", side_effect=RuntimeError):
            response = self.call(client, {"access_token": "a", "refresh_token": "r"})

        assert response.url == reverse("dashboard_profile")
        assert PatreonAccountBind.objects.filter(user=user).exists()

    def test_missing_tokens_reports_error(self, client, user):
        client.force_login(user)
        response = self.call(client, {"error": "invalid_grant"})

        assert response.url == reverse("dashboard_profile") + "?link_error=patreon"
        assert not PatreonAccountBind.objects.filter(user=user).exists()

    def test_token_exchange_crash_reports_error(self, client, user):
        client.force_login(user)
        with mock.patch("aiarena.patreon.views.PatreonOAuth.get_tokens", side_effect=RuntimeError):
            response = client.get(reverse("patreon_oauth_redirect"), {"code": "abc"})

        assert response.url == reverse("dashboard_profile") + "?link_error=patreon"
        assert not PatreonAccountBind.objects.filter(user=user).exists()

    def test_cancelled_consent_is_not_an_error(self, client, user):
        client.force_login(user)
        response = self.call(client, {}, params={"error": "access_denied"})

        assert response.url == reverse("dashboard_profile")
        assert not PatreonAccountBind.objects.filter(user=user).exists()

    @pytest.mark.django_db
    def test_anonymous_is_sent_to_login(self, client):
        response = self.call(client, {"access_token": "a", "refresh_token": "r"})

        assert response.status_code == 302
        assert response.url.startswith(reverse("login"))
        assert not PatreonAccountBind.objects.exists()
