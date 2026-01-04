from django.test import TransactionTestCase

from constance import config
from rest_framework.authtoken.models import Token

from aiarena.core.models import ArenaClient, GameMode, Map, Match, User
from aiarena.core.models.bot_race import BotRace
from aiarena.core.services import bots, match_requests
from aiarena.core.tests.test_mixins import LoggedInMixin
from aiarena.core.utils import calculate_md5


class MatchesTestCase(LoggedInMixin, TransactionTestCase):
    def setUp(self):
        super().setUp()
        self.regularUser2 = User.objects.create_user(
            username="regular_user2", password="x", email="regular_user2@aiarena.net"
        )

    def test_get_next_match_not_authorized(self):
        self.test_ac_api_client.set_api_token("")
        self._post_to_matches(expected_code=403)

        # create and use a regular user's api token
        self.test_ac_api_client.set_api_token(Token.objects.create(user=self.regularUser1).key)
        self._post_to_matches(expected_code=403)

    def test_post_next_match(self):
        # avoid old tests breaking that were pre-this feature
        config.REISSUE_UNFINISHED_MATCHES = False

        self.test_client.login(self.staffUser1)

        # no current competition
        self._post_to_matches(expected_code=200)

        # needs a valid competition to be able to activate a bot.
        comp = self._create_game_mode_and_open_competition()

        # no maps
        response = self._post_to_matches(expected_code=200)
        self.assertEqual("no_game_available", response.data["detail"].code)

        # not enough active bots
        self._create_map_for_competition("test_map", comp.id)
        response = self._post_to_matches(expected_code=200)
        self.assertEqual("no_game_available", response.data["detail"].code)

        # not enough active bots
        bot1 = self._create_bot(self.regularUser1, "testbot1")
        response = self._post_to_matches(expected_code=200)
        self.assertEqual("no_game_available", response.data["detail"].code)

        # not enough active bots
        bot2 = self._create_bot(self.regularUser1, "testbot2")
        response = self._post_to_matches(expected_code=200)
        self.assertEqual("no_game_available", response.data["detail"].code)

        # not enough active bots
        bot1.competition_participations.create(competition=comp)
        response = self._post_to_matches(expected_code=200)
        self.assertEqual("no_game_available", response.data["detail"].code)

        # success
        bot2.competition_participations.create(competition=comp)
        response = self._post_to_matches()

        # test download files

        # zip
        bot1_zip = self.client.get(response.data["bot1"]["bot_zip"])
        bot1_zip_path = "./tmp/bot1.zip"
        with open(bot1_zip_path, "wb") as bot1_zip_file:  # todo: this can probably be done without saving to file
            self._write_file_response_to_file(bot1_zip, bot1_zip_file)
        self.assertEqual(response.data["bot1"]["bot_zip_md5hash"], calculate_md5(bot1_zip_path))

        bot1_zip = self.client.get(response.data["bot2"]["bot_zip"])
        bot1_zip_path = "./tmp/bot2.zip"
        with open(bot1_zip_path, "wb") as bot1_zip_file:
            self._write_file_response_to_file(bot1_zip, bot1_zip_file)
        self.assertEqual(response.data["bot2"]["bot_zip_md5hash"], calculate_md5(bot1_zip_path))

        # data
        bot1_zip = self.client.get(response.data["bot1"]["bot_data"])
        bot1_zip_path = "./tmp/bot1_data.zip"
        with open(bot1_zip_path, "wb") as bot1_zip_file:
            self._write_file_response_to_file(bot1_zip, bot1_zip_file)
        self.assertEqual(response.data["bot1"]["bot_data_md5hash"], calculate_md5(bot1_zip_path))

        bot1_zip = self.client.get(response.data["bot2"]["bot_data"])
        bot1_zip_path = "./tmp/bot2_data.zip"
        with open(bot1_zip_path, "wb") as bot1_zip_file:
            self._write_file_response_to_file(bot1_zip, bot1_zip_file)
        self.assertEqual(response.data["bot2"]["bot_data_md5hash"], calculate_md5(bot1_zip_path))

        # not enough available bots
        self._post_to_matches(expected_code=200)

        # ensure only 1 match was created
        self.assertEqual(Match.objects.count(), 1)

    def _write_file_response_to_file(self, file_response, file):
        # we need to do this because, if the file backend is S3, it will be a streaming response
        # otherwise it will be a regular response
        # This enables the tests to run against S3 or local file storage
        if hasattr(file_response, "streaming_content"):
            self._write_streaming_content_to_file(file_response.streaming_content, file)
        else:
            self._write_content_to_file(file_response.content, file)

    def _write_streaming_content_to_file(self, streaming_content, file):
        for chunk in streaming_content:
            file.write(chunk)

    def _write_content_to_file(self, content, file):
        file.write(content)
        file.close()

    def test_match_reissue(self):
        self.test_client.login(self.staffUser1)
        comp = self._create_game_mode_and_open_competition()
        self._create_map_for_competition("test_map", comp.id)

        self._create_active_bot_for_competition(comp.id, self.regularUser1, "testbot1", BotRace.terran())
        self._create_active_bot_for_competition(comp.id, self.regularUser1, "testbot2", BotRace.zerg())

        # currently we should be using arenaclientUser1's token
        response_m1 = self.test_ac_api_client.post_to_matches()

        # should be the same match reissued
        response_m2 = self.test_ac_api_client.post_to_matches()

        self.assertEqual(response_m1.data["id"], response_m2.data["id"])

    def test_match_requests_no_open_competition(self):
        """
        Tests that match requests still run when no competitions are open.
        :return:
        """

        self.test_client.login(self.staffUser1)
        game = self.test_client.create_game("StarCraft II", ".SC2Map")
        game_mode = self.test_client.create_gamemode("Melee", game.id)
        BotRace.create_all_races()
        Map.objects.create(name="testmap", game_mode=game_mode)

        bot1 = self._create_bot(self.regularUser1, "testbot1", BotRace.terran())
        self._create_bot(self.regularUser1, "testbot2", BotRace.zerg())

        # self.test_client.login(self.arenaclientUser1)

        # we shouldn't be able to get a new match
        response = self._post_to_matches(expected_code=200)
        self.assertEqual("no_game_available", response.data["detail"].code)

        match_requests.request_match(self.regularUser2, bot1, bot1.get_random_excluding_self(), game_mode=game_mode)

        # now we should be able to get a match - the requested one
        self._post_to_matches()

    def test_max_active_rounds(self):
        # we don't want to have to create lots of arenaclients for multiple matches
        config.REISSUE_UNFINISHED_MATCHES = False

        self.test_client.login(self.staffUser1)

        # competitions will default to max 2 active rounds
        comp = self._create_game_mode_and_open_competition()
        self._create_map_for_competition("test_map", comp.id)

        self._create_active_bot_for_competition(comp.id, self.regularUser1, "testbot1", BotRace.terran())
        self._create_active_bot_for_competition(comp.id, self.regularUser1, "testbot2", BotRace.zerg())
        self._create_active_bot_for_competition(comp.id, self.regularUser1, "testbot3", BotRace.protoss())
        self._create_active_bot_for_competition(comp.id, self.regularUser1, "testbot4", BotRace.random())

        # Round 1
        # self.test_client.login(self.arenaclientUser1)
        self._post_to_matches()
        match_id = self._post_to_matches().data["id"]
        self._post_to_results(match_id, "Player1Win")

        # Match 1 has started, Match 2 is finished.

        # Round 2
        match_id = self._post_to_matches().data["id"]
        self._post_to_results(match_id, "Player1Win")

        # Round 3 - should fail due to active round limit
        with self.assertLogs(logger="aiarena.api.arenaclient.common.ac_coordinator", level="DEBUG") as log:
            response = self._post_to_matches(expected_code=200)
            self.assertTrue("detail" in response.data)
            self.assertEqual("No game available for client.", response.data["detail"])
            self.assertIn(
                f"DEBUG:aiarena.api.arenaclient.common.ac_coordinator:Skipping competition {comp.id}: "
                "This competition has reached it's maximum active rounds.",
                log.output,
            )

    def test_match_blocking(self):
        # create an extra arena client for this test
        self.arenaclientUser2 = ArenaClient.objects.create(
            username="arenaclient2",
            email="arenaclient2@dev.aiarena.net",
            type="ARENA_CLIENT",
            trusted=True,
            owner=self.staffUser1,
        )

        self.test_client.login(self.staffUser1)
        comp = self._create_game_mode_and_open_competition()
        self._create_map_for_competition("test_map", comp.id)

        bot1 = self._create_active_bot_for_competition(comp.id, self.regularUser1, "testbot1", BotRace.terran())
        self._create_active_bot_for_competition(comp.id, self.regularUser1, "testbot2", BotRace.zerg())

        # at this point we are using arenaclientUser1's token
        # this should tie up both bots
        self.test_ac_api_client.post_to_matches()

        # we shouldn't be able to get a new match
        self.test_ac_api_client.set_api_token(Token.objects.create(user=self.arenaclientUser2).key)

        with self.assertLogs(logger="aiarena.api.arenaclient.common.ac_coordinator", level="DEBUG") as log:
            response = self.test_ac_api_client.post_to_matches(expected_code=200)
            self.assertEqual("No game available for client.", response.data["detail"])
            self.assertIn(
                f"DEBUG:aiarena.api.arenaclient.common.ac_coordinator:Skipping competition {comp.id}: "
                f"Not enough available bots for a match. Wait until more bots become available.",
                log.output,
            )

        match_requests.request_match(
            self.regularUser2,
            bot1,
            bots.get_random_active_bot_excluding(bot1.id),
            game_mode=GameMode.objects.first(),
        )

        # now we should be able to get a match - the requested one
        self.test_ac_api_client.post_to_matches()

    def test_untrusted_competition(self):
        untrustedClient = ArenaClient.objects.create(
            username="untrustedclient",
            email="untrustedclient@dev.aiarena.net",
            type="ARENA_CLIENT",
            trusted=False,
            owner=self.staffUser1,
        )
        # we don't want to have to create lots of arenaclients for multiple matches
        config.REISSUE_UNFINISHED_MATCHES = False

        self.test_client.login(self.staffUser1)
        # competitions will default to max 2 active rounds
        comp = self._create_game_mode_and_open_competition(trusted=False)
        self._create_map_for_competition("test_map", comp.id)

        self._create_active_bot_for_competition(
            comp.id, self.regularUser1, "testbot1", BotRace.terran(), downloadable=True
        )
        self._create_active_bot_for_competition(
            comp.id, self.regularUser1, "testbot2", BotRace.zerg(), downloadable=True
        )
        self._create_active_bot_for_competition(
            comp.id, self.regularUser1, "testbot3", BotRace.protoss(), downloadable=True
        )
        self._create_active_bot_for_competition(
            comp.id, self.regularUser1, "testbot4", BotRace.random(), downloadable=True
        )

        # Round 1
        self.test_ac_api_client.set_api_token(Token.objects.create(user=untrustedClient).key)
        self._post_to_matches()
        match_id = self._post_to_matches().data["id"]
        self._post_to_results(match_id, "Player1Win")
