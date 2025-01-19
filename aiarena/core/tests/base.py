import json
from http import HTTPStatus
from urllib.parse import urlparse, urlunparse

from django.core.serializers.json import DjangoJSONEncoder
from django.http import HttpResponse
from django.test import Client
from django.urls import reverse

from pytest_django.live_server_helper import LiveServer

from aiarena.core.models import WebsiteUser
from aiarena.core.utils import dict_camel_case, dict_get


class BrowserHelper:
    def __init__(self, live_server: LiveServer):
        self.live_server = live_server

    def reverse(self, *args, **kwargs):
        url = reverse(*args, **kwargs)
        parsed = urlparse(url)
        if not parsed.netloc:
            live = urlparse(self.live_server.url)
            parsed = parsed._replace(scheme=live.scheme, netloc=live.netloc)
        return urlunparse(parsed)


class GraphQLTest:
    """
    Helper class with methods for testing GraphQL API.
    """

    # GraphQL mutation query used by `mutate` method.
    mutation = None
    # stored django test client for the last performed query, makes it possible
    # to check request/response attributes (like auth session)
    last_query_client = None

    def mutate(
        self,
        expected_status: int = 200,
        mutation: str | None = None,
        login_user: WebsiteUser | None = None,
        **kwargs,
    ) -> dict | None:
        """
        Perform GraphQL mutation.
        """
        kwargs = dict_camel_case(kwargs)
        return self.query(
            query=(mutation or self.mutation),
            expected_status=expected_status,
            login_user=login_user,
            variables=kwargs,
        )

    def query(
        self,
        query: str,
        expected_status: int = HTTPStatus.OK.value,
        variables: dict | None = None,
        login_user: WebsiteUser | None = None,
    ) -> dict | None:
        """Perform GraphQL query."""
        self.last_query_client = self.client(login_user)
        response = self.do_post(self.last_query_client, query, variables)
        assert response.status_code == expected_status, (
            f"Unexpected response status code: {response.status_code}\n" f"Response content: {response.content}"
        )
        if response.status_code == HTTPStatus.OK.value:
            return json.loads(response.content)

    @classmethod
    def client(
        cls,
        login_user: WebsiteUser | None = None,
    ) -> Client:
        """
        Create django HTTP client.
        """
        client = Client()
        if login_user:
            client.force_login(login_user)

        return client

    @classmethod
    def assert_graphql_error(cls, response: dict, message: str):
        """
        Check GQL response contains given error message.
        """
        assert "errors" in response
        messages = {error["message"] for error in response["errors"]}
        if message not in messages:
            msg = f'Expected to find "{message}" error, but found: {messages}'
            raise AssertionError(msg)

    @classmethod
    def assert_graphql_error_like(cls, response: dict, substring: str):
        """
        Check GQL response contains given error message.
        """
        assert "errors" in response
        messages = {error["message"] for error in response["errors"]}
        for message in messages:
            if substring in message:
                return
        msg = '"{}" wasn\'t found in error messages:\n{}'.format(
            substring,
            "\n".join(f" - {m}" for m in messages),
        )
        raise AssertionError(msg)

    @classmethod
    def assert_no_graphql_errors(cls, response: dict):
        """
        Check GQL response does not contain any errors.
        """
        err = {error["message"] for error in response.get("errors", [])}
        msg = f"Expected no errors, but got: {err}"
        assert not err, msg

    @classmethod
    def assert_access_denied(cls, response: dict):
        cls.assert_graphql_error(response, "Access denied.")

    @classmethod
    def do_post(
        cls,
        client: Client,
        query: str,
        variables: dict | None,
    ) -> HttpResponse:
        """
        Perform POST-request to the GraphQL api.
        """
        return client.post(
            reverse("graphql"),
            data=json.dumps(
                {
                    "query": query,
                    "variables": (variables or {}),
                },
                cls=DjangoJSONEncoder,
            ),
            content_type="application/json",
        )

    @staticmethod
    def nodes(response, path):
        """
        Unwraps pure objects from edges/nodes connection.
        :param response: dict returned by query
        :param path: string like viewer.currentOrganization.onboardingTasks
        :return: unwrapped objects
        """
        root = response.get("data", response)
        connection = dict_get(root, path)
        if not connection:
            return []
        return [edge["node"] for edge in connection["edges"]]
