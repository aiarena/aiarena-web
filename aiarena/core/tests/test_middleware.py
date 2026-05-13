from unittest import mock

from django.contrib.auth.models import AnonymousUser
from django.test import RequestFactory

import pytest
from rest_framework.authtoken.models import Token

from aiarena.core.middleware import graphql_token_auth
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
