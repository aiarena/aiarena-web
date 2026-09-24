from urllib.parse import parse_qs, urlparse

from django.core.files.base import ContentFile

import pytest
import requests

from aiarena.core.tests.base import GraphQLTest
from aiarena.graphql import BotType


class TestBotFileUrls(GraphQLTest):
    """botZipUrl / botDataUrl hand out presigned S3 download URLs, gated on who may download the file."""

    # language=graphql
    query_text = """
        query ($id: ID!) {
            node(id: $id) {
                ... on BotType {
                    botZipUrl
                    botDataUrl
                }
            }
        }
    """

    @pytest.fixture
    def bot_with_data(self, bot):
        bot.bot_data = ContentFile(b"bot data", name="data.zip")
        bot.save()
        return bot

    def _file_urls(self, bot, login_user=None) -> dict:
        return self.query(
            self.query_text,
            variables={"id": self.to_global_id(BotType, bot.id)},
            login_user=login_user,
        )["node"]

    def test_owner_gets_working_presigned_urls(self, bot_with_data, user):
        urls = self._file_urls(bot_with_data, login_user=user)

        bot_zip_response = requests.get(urls["botZipUrl"])
        bot_zip_response.raise_for_status()
        assert bot_zip_response.content == bot_with_data.bot_zip.read()
        assert requests.get(urls["botDataUrl"]).content == b"bot data"

        # The file downloads under the bot's name, not its storage key.
        query = parse_qs(urlparse(urls["botDataUrl"]).query)
        assert query["response-content-disposition"] == [f'inline; filename="{bot_with_data.name}_data.zip"']

    def test_other_user_gets_no_urls(self, bot_with_data, other_user):
        assert self._file_urls(bot_with_data, login_user=other_user) == {"botZipUrl": None, "botDataUrl": None}

    def test_anonymous_user_gets_no_urls(self, bot_with_data):
        assert self._file_urls(bot_with_data) == {"botZipUrl": None, "botDataUrl": None}

    def test_publicly_downloadable_files_are_available_to_anyone(self, bot_with_data):
        bot_with_data.bot_zip_publicly_downloadable = True
        bot_with_data.bot_data_publicly_downloadable = True
        bot_with_data.save()

        urls = self._file_urls(bot_with_data)
        assert urls["botZipUrl"] is not None
        assert urls["botDataUrl"] is not None

    def test_no_bot_data_means_no_url(self, bot, user):
        assert self._file_urls(bot, login_user=user)["botDataUrl"] is None
