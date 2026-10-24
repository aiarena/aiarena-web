from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from constance.test import override_config
from rest_framework import status
from rest_framework.test import APIClient

from aiarena.core.models import Map, Match
from aiarena.core.tests.test_mixins import MatchReadyMixin


User = get_user_model()


class MatchRequestsViewSetTests(MatchReadyMixin, TestCase):
    def setUp(self):
        super().setUp()
        self.client = APIClient()
        self.client.force_authenticate(user=self.regularUser1)

        # Create test map
        self.test_map = Map.objects.first()

        self.url = reverse("api_request_match-request-single")

    def test_request_match_failure_not_supporter(self):
        """Test match request failure - user is not a supporter"""
        user = self.staffUser1
        user.patreon_level = "none"
        response = self.request_match(user)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(Match.objects.count(), 0)

    def test_request_match_success_supporter(self):
        """Test match request successful - user is a supporter"""
        user = self.staffUser1
        user.patreon_level = "bronze"
        response = self.request_match(user)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn("match_id", response.data)
        self.assertEqual(Match.objects.count(), 1)
        match = Match.objects.first()
        self.assertEqual(match.requested_by, User.objects.get(id=user.id))
        self.assertEqual(match.map, self.test_map)

    def request_match(self, user, **extra):
        data = {
            "bot1": self.regularUser1Bot1.id,
            "bot2": self.regularUser1Bot2.id,
            "map": self.test_map.id,
            **extra,
        }
        self.client.force_authenticate(user=user)
        return self.client.post(self.url, data, format="json")

    @override_config(ALLOW_MATCH_REQUEST_BOT_ARGS=True)
    def test_request_match_with_bot_args(self):
        """The scripted path a tournament organiser would use has to be able to
        set bot arguments, not just the web UI."""
        user = self.staffUser1
        user.patreon_level = "bronze"
        response = self.request_match(user, bot1_args="--tournament=worldcup", bot2_args='--build="all in"')

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        match = Match.objects.get(id=response.data["match_id"])
        self.assertEqual(match.bot1_args, "--tournament=worldcup")
        self.assertEqual(match.bot2_args, '--build="all in"')

    def test_request_match_without_bot_args(self):
        user = self.staffUser1
        user.patreon_level = "bronze"
        response = self.request_match(user)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        match = Match.objects.get(id=response.data["match_id"])
        self.assertEqual(match.bot1_args, "")
        self.assertEqual(match.bot2_args, "")

    def test_request_match_bot_args_rejected_while_disabled(self):
        """Same rejection as the GraphQL mutation gives - both APIs run the
        same cleaner, so they can't drift apart."""
        user = self.staffUser1
        user.patreon_level = "bronze"
        response = self.request_match(user, bot1_args="--tournament=worldcup")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data["bot1_args"], ["Bot arguments are currently disabled."])
        self.assertEqual(Match.objects.count(), 0)

    @override_config(ALLOW_MATCH_REQUEST_BOT_ARGS=True)
    def test_request_match_bot_args_rejects_unclosed_quote(self):
        user = self.staffUser1
        user.patreon_level = "bronze"
        response = self.request_match(user, bot1_args='--message="oops')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data["bot1_args"], ["Could not be split into arguments: No closing quotation."])
        self.assertEqual(Match.objects.count(), 0)

    def test_request_match_invalid_bot(self):
        """Test match request with invalid bot ID"""
        data = {
            "bot1": 99999,  # Non-existent bot ID
            "bot2": self.regularUser1Bot2.id,
        }

        user = self.staffUser1
        user.patreon_level = "bronze"
        self.client.force_authenticate(user=user)
        response = self.client.post(self.url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(Match.objects.count(), 0)

    def test_request_match_unauthenticated(self):
        """Test match request without authentication"""
        self.client.force_authenticate(user=None)

        data = {
            "bot1": self.regularUser1Bot1.id,
            "bot2": self.regularUser1Bot2.id,
        }

        response = self.client.post(self.url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(Match.objects.count(), 0)
