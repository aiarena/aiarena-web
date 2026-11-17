from datetime import timedelta
from urllib.parse import parse_qs, urlparse

from django.core.files.base import ContentFile
from django.utils import timezone

import pytest
import requests

from aiarena.core.models import Match, MatchParticipation, Round
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


class TestBotRequestedMatches(GraphQLTest):
    """requestedMatches lists the bot's matches outside any competition round, wherever it sits in the match."""

    # language=graphql
    query_text = """
        query ($id: ID!) {
            node(id: $id) {
                ... on BotType {
                    requestedMatches {
                        edges { node { databaseId requestedBy { username } } }
                    }
                }
            }
        }
    """

    def _match(self, bot1, bot2, map, *, round=None, requested_by=None, started=None):
        match = Match.objects.create(map=map, round=round, requested_by=requested_by, started=started)
        MatchParticipation.objects.create(match=match, participant_number=1, bot=bot1)
        MatchParticipation.objects.create(match=match, participant_number=2, bot=bot2)
        return match

    def _requested(self, bot) -> list[dict]:
        data = self.query(self.query_text, variables={"id": self.to_global_id(BotType, bot.id)})
        return [edge["node"] for edge in data["node"]["requestedMatches"]["edges"]]

    def test_lists_requested_matches_on_either_side_newest_first(
        self, bot, other_bot, bot_factory, user, other_user, map, competition
    ):
        now = timezone.now()
        third_bot = bot_factory(other_user, "Third_Bot")
        as_participant1 = self._match(bot, other_bot, map, requested_by=user, started=now - timedelta(hours=1))
        as_participant2 = self._match(other_bot, bot, map, requested_by=other_user, started=now)
        self._match(bot, other_bot, map, round=Round.objects.create(competition=competition))  # competition game
        self._match(other_bot, third_bot, map, requested_by=user)  # doesn't involve this bot

        assert self._requested(bot) == [
            {"databaseId": as_participant2.id, "requestedBy": {"username": other_user.username}},
            {"databaseId": as_participant1.id, "requestedBy": {"username": user.username}},
        ]

    def test_keeps_matches_whose_requester_was_deleted(self, bot, other_bot, map):
        """requested_by is SET_NULL, so "outside a round" is what makes a match a requested one."""
        match = self._match(bot, other_bot, map, requested_by=None)

        assert self._requested(bot) == [{"databaseId": match.id, "requestedBy": None}]

    def test_excludes_matches_older_than_a_year(self, bot, other_bot, user, map):
        recent = self._match(bot, other_bot, map, requested_by=user)
        old = self._match(bot, other_bot, map, requested_by=user)
        Match.objects.filter(id=old.id).update(created=timezone.now() - timedelta(days=400))

        assert self._requested(bot) == [{"databaseId": recent.id, "requestedBy": {"username": user.username}}]
