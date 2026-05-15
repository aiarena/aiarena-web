from unittest import mock

from django.contrib.auth.models import AnonymousUser
from django.test import RequestFactory
from django.urls import reverse

import pytest
from rest_framework.authtoken.models import Token
from rest_framework.test import APIClient

from aiarena.core.middleware import API_USAGE_KEY_PREFIX, graphql_token_auth
from aiarena.core.models import ArenaClient


@pytest.fixture
def arenaclient_user(db, admin_user):
    return ArenaClient.objects.create(
        username="ac1",
        email="ac1@dev.aiarena.net",
        type="ARENA_CLIENT",
        trusted=True,
        owner=admin_user,
    )


@pytest.fixture
def arenaclient_token(arenaclient_user):
    return Token.objects.create(user=arenaclient_user).key


def _make_middleware():
    """Build the middleware with a get_response that records what it sees."""
    seen = {}

    def get_response(request):
        seen["request"] = request
        seen["user"] = request.user
        return mock.sentinel.response

    return graphql_token_auth(get_response), seen


class TestGraphQLTokenAuthMiddleware:
    def test_valid_token_populates_user(self, arenaclient_user, arenaclient_token):
        middleware, seen = _make_middleware()
        request = RequestFactory().post(
            "/graphql/",
            HTTP_AUTHORIZATION=f"Token {arenaclient_token}",
        )
        request.user = AnonymousUser()

        response = middleware(request)

        assert response is mock.sentinel.response
        # Token.user returns a base User; same row, different Python class than ArenaClient.
        assert seen["user"].pk == arenaclient_user.pk
        assert seen["user"].is_authenticated

    def test_valid_token_disables_csrf(self, arenaclient_user, arenaclient_token):
        """Token-authenticated requests must bypass CSRF — REST clients have no CSRF cookie."""
        middleware, seen = _make_middleware()
        request = RequestFactory().post(
            "/graphql/",
            HTTP_AUTHORIZATION=f"Token {arenaclient_token}",
        )
        request.user = AnonymousUser()

        middleware(request)

        assert getattr(seen["request"], "_dont_enforce_csrf_checks", False) is True

    def test_bad_token_does_not_disable_csrf(self, db):
        """A bad token must NOT disable CSRF — otherwise the header alone would bypass it."""
        middleware, seen = _make_middleware()
        request = RequestFactory().post(
            "/graphql/",
            HTTP_AUTHORIZATION="Token not-a-real-token",
        )
        request.user = AnonymousUser()

        middleware(request)

        assert getattr(seen["request"], "_dont_enforce_csrf_checks", False) is False

    def test_bad_token_leaves_anonymous(self, db):
        middleware, seen = _make_middleware()
        request = RequestFactory().post(
            "/graphql/",
            HTTP_AUTHORIZATION="Token not-a-real-token",
        )
        request.user = AnonymousUser()

        middleware(request)

        assert seen["user"].is_anonymous

    def test_missing_authorization_header_leaves_anonymous(self, db):
        middleware, seen = _make_middleware()
        request = RequestFactory().post("/graphql/")
        request.user = AnonymousUser()

        middleware(request)

        assert seen["user"].is_anonymous

    def test_non_token_scheme_is_ignored(self, db):
        """A `Bearer` or `Basic` header is not for us — leave anonymous, don't error."""
        middleware, seen = _make_middleware()
        request = RequestFactory().post(
            "/graphql/",
            HTTP_AUTHORIZATION="Bearer something-else",
        )
        request.user = AnonymousUser()

        middleware(request)

        assert seen["user"].is_anonymous

    def test_already_authenticated_user_not_overwritten(self, arenaclient_user, arenaclient_token, admin_user):
        """If session auth already set request.user, the middleware leaves it alone."""
        middleware, seen = _make_middleware()
        request = RequestFactory().post(
            "/graphql/",
            HTTP_AUTHORIZATION=f"Token {arenaclient_token}",
        )
        request.user = admin_user  # pretend session auth ran

        middleware(request)

        assert seen["user"] == admin_user

    def test_non_graphql_path_skipped_without_db_hit(self, arenaclient_token):
        """The middleware must not run token auth for non-/graphql paths.

        We assert this by intercepting TokenAuthentication.authenticate — if the
        middleware short-circuits on path, this is never called.
        """
        middleware, seen = _make_middleware()
        request = RequestFactory().get(
            "/api/something-else/",
            HTTP_AUTHORIZATION=f"Token {arenaclient_token}",
        )
        request.user = AnonymousUser()

        with mock.patch("aiarena.core.middleware.TokenAuthentication.authenticate") as authenticate:
            middleware(request)

        authenticate.assert_not_called()
        assert seen["user"].is_anonymous


class TestApiUsageTrackingMiddleware:
    """End-to-end checks that the middleware records token-authenticated API calls.

    We patch celery_redis.rpush so we don't need a live Redis — the assertion is
    that rpush was called, with a key matching our scheme.
    """

    @staticmethod
    def _key_user_ids(rpush_mock):
        ids = []
        for call in rpush_mock.call_args_list:
            key = call.args[0]
            assert key.startswith(f"{API_USAGE_KEY_PREFIX}:"), key
            ids.append(int(key.rsplit(":", 1)[1]))
        return ids

    def test_rest_api_call_records_usage(self, arenaclient_user, arenaclient_token):
        client = APIClient()
        client.credentials(HTTP_AUTHORIZATION=f"Token {arenaclient_token}")

        with mock.patch("aiarena.core.middleware.celery_redis.rpush") as rpush:
            response = client.get(reverse("api_bot-list"))

        assert response.status_code == 200, response.content
        assert rpush.called
        assert self._key_user_ids(rpush) == [arenaclient_user.pk]

    def test_graphql_call_records_usage(self, arenaclient_user, arenaclient_token):
        client = APIClient()

        with mock.patch("aiarena.core.middleware.celery_redis.rpush") as rpush:
            response = client.post(
                reverse("graphql"),
                data={"query": "{ viewer { user { id } } }"},
                format="json",
                HTTP_AUTHORIZATION=f"Token {arenaclient_token}",
            )

        assert response.status_code == 200, response.content
        # Sanity check that the token actually authenticated us — the viewer field
        # is null/errored when anonymous, so non-null user.id is a reliable signal.
        body = response.json()
        assert body.get("data", {}).get("viewer", {}).get("user", {}).get("id"), body
        assert rpush.called
        assert self._key_user_ids(rpush) == [arenaclient_user.pk]

    def test_unauthenticated_request_does_not_record(self, db):
        """Hitting the homepage with no token must not write to Redis."""
        client = APIClient()

        with mock.patch("aiarena.core.middleware.celery_redis.rpush") as rpush:
            client.get("/")

        rpush.assert_not_called()

    def test_session_authenticated_request_does_not_record(self, user):
        """We only count token-auth API usage. A logged-in browser session is not API traffic."""
        client = APIClient()
        client.force_login(user)

        with mock.patch("aiarena.core.middleware.celery_redis.rpush") as rpush:
            client.get("/")

        rpush.assert_not_called()
