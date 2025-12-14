import json
from http import HTTPStatus
from urllib.parse import urlparse, urlunparse

from django.http import HttpResponse
from django.test import Client
from django.urls import reverse

import graphene
from playwright.sync_api import Page
from pytest_django.live_server_helper import LiveServer

from aiarena.core.models import WebsiteUser
from aiarena.core.utils import dict_get


class BrowserHelper:
    def __init__(self, live_server: LiveServer):
        self.live_server = live_server

    def reverse(self, *args, **kwargs):
        url = reverse(*args, **kwargs)
        parsed = urlparse(url)
        if not parsed.netloc:
            live = urlparse(self.live_server.url)
            parsed = parsed._replace(scheme=live.scheme, netloc=live.netloc)
        return str(urlunparse(parsed))

    def log_in(self, user: WebsiteUser, page: Page):
        page.goto(self.reverse("login"))
        page.get_by_label("Username:").fill("billy")
        page.get_by_label("Password:").fill("guest")
        page.get_by_role("button", name="Log in").click()


class GraphQLTest:
    """
    Helper class with methods for testing GraphQL API.
    """

    # GraphQL mutation query used by `mutate` method.
    mutation = None
    # The mutation's name so that we can get the content from the JSON response
    mutation_name = None
    # stored django test client for the last performed query, makes it possible
    # to check request/response attributes (like auth session)
    last_query_client = None

    def mutate(
        self,
        variables: dict = None,
        expected_status: int = HTTPStatus.OK.value,
        mutation: str | None = None,
        login_user: WebsiteUser | None = None,
        expected_validation_errors=None,
        **kwargs,
    ) -> dict | None:
        """
        Perform GraphQL mutation.
        """
        expected_validation_errors = expected_validation_errors or {}
        response_data = self.query(
            query=(mutation or self.mutation),
            expected_status=expected_status,
            login_user=login_user,
            variables=variables,
            **kwargs,
        )

        if response_data:
            mutation_data = response_data[self.mutation_name] or {}
        else:
            mutation_data = {}
        actual_errors = {error["field"]: error["messages"] for error in mutation_data.get("errors", [])}
        assert actual_errors == expected_validation_errors, (
            f"Unexpected validation errors: {actual_errors}, expected {expected_validation_errors}"
        )

        return response_data

    def query(
        self,
        query: str,
        expected_status: int = HTTPStatus.OK.value,
        expected_errors_like: list = None,
        variables: dict | None = None,
        login_user: WebsiteUser | None = None,
        **kwargs,
    ) -> dict | None:
        """Perform GraphQL query."""
        expected_errors_like = expected_errors_like or []

        self.last_query_client = self.client(login_user)

        response = self.do_post(self.last_query_client, query, variables, **kwargs)

        assert response.status_code == expected_status, (
            f"Unexpected response status code: {response.status_code}\nResponse content: {response.content}"
        )

        content = json.loads(response.content)
        error_messages = [error["message"] for error in content.get("errors", [])]
        found = []

        for message in expected_errors_like:
            for error in error_messages:
                if message in error:
                    found.append(error)
                    break
            else:
                raise ValueError(f"Unexpected errors: {error_messages}\nResponse content: {content}")
        unexpected = set(error_messages) - set(found)
        assert not unexpected, f"Unexpected errors: {unexpected}"

        if response.status_code == HTTPStatus.OK.value:
            return json.loads(response.content)["data"]

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
    def do_post(
        cls,
        client: Client,
        query: str,
        variables=None,
        files=None,
        headers=None,
    ) -> HttpResponse:
        """
        Perform POST-request to the GraphQL api.
        """

        headers = headers or {}
        files = files or {}
        variables = variables or {}
        map_ = {}

        for key in files.keys():
            map_[key] = [f"variables.{key}"]
            if key not in variables:
                variables[key] = None

        body = {"query": query}
        if variables:
            body["variables"] = variables

        data = {
            "operations": json.dumps(body),
            "map": json.dumps(map_),
            **files,
        }

        return client.post(reverse("graphql"), data, **headers)

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

    @staticmethod
    def to_global_id(type_, id_: str):
        return graphene.Node.to_global_id(type_, id_)
