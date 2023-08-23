import io
import json
import os

from django.db.models import Sum
from django.test import TransactionTestCase

import jsonschema
from constance import config
from rest_framework.authtoken.models import Token

from aiarena.core.api import Matches
from aiarena.core.models import (
    ArenaClient,
    Bot,
    BotCrashLimitAlert,
    Competition,
    CompetitionParticipation,
    Map,
    Match,
    MatchParticipation,
    Result,
    Round,
    User,
)
from aiarena.core.models.bot_race import BotRace
from aiarena.core.models.game_mode import GameMode
from aiarena.core.tests.test_mixins import LoggedInMixin, MatchReadyMixin
from aiarena.core.tests.testing_utils import TestAssetPaths
from aiarena.core.utils import calculate_md5
from aiarena.settings import BASE_DIR, ELO_START_VALUE, MEDIA_ROOT, PRIVATE_STORAGE_ROOT


class MatchesTestCase(LoggedInMixin, TransactionTestCase):
    def setUp(self):
        super(MatchesTestCase, self).setUp()
        self.regularUser2 = User.objects.create_user(
            username="regular_user2", password="x", email="regular_user2@aiarena.net"
        )

    def test_get_next_match_not_authorized(self):
        self.test_ac_api_client.set_api_token("")
        response = self._post_to_matches()
        self.assertEqual(response.status_code, 403)

        # create and use a regular user's api token
        self.test_ac_api_client.set_api_token(Token.objects.create(user=self.regularUser1).key)
        response = self._post_to_matches()
        self.assertEqual(response.status_code, 403)

    def test_post_next_match(self):
        # avoid old tests breaking that were pre-this feature
        config.REISSUE_UNFINISHED_MATCHES = False

        self.test_client.login(self.staffUser1)

        # no current competition
        response = self._post_to_matches()
        self.assertEqual(response.status_code, 200, f"{response.status_code} {response.data}")

        # needs a valid competition to be able to activate a bot.
        comp = self._create_game_mode_and_open_competition()

        # no maps
        response = self._post_to_matches()
        self.assertEqual(response.status_code, 200)
        self.assertEqual("no_game_available", response.data["detail"].code)

        # not enough active bots
        self._create_map_for_competition("test_map", comp.id)
        response = self._post_to_matches()
        self.assertEqual(response.status_code, 200)
        self.assertEqual("no_game_available", response.data["detail"].code)

        # not enough active bots
        bot1 = self._create_bot(self.regularUser1, "testbot1")
        response = self._post_to_matches()
        self.assertEqual(response.status_code, 200)
        self.assertEqual("no_game_available", response.data["detail"].code)

        # not enough active bots
        bot2 = self._create_bot(self.regularUser1, "testbot2")
        response = self._post_to_matches()
        self.assertEqual(response.status_code, 200)
        self.assertEqual("no_game_available", response.data["detail"].code)

        # not enough active bots
        bot1.competition_participations.create(competition=comp)
        response = self._post_to_matches()
        self.assertEqual(response.status_code, 200)
        self.assertEqual("no_game_available", response.data["detail"].code)

        # success
        bot2.competition_participations.create(competition=comp)
        response = self._post_to_matches()
        self.assertEqual(response.status_code, 201)

        # test download files

        # zip
        bot1_zip = self.client.get(response.data["bot1"]["bot_zip"])
        bot1_zip_path = "./tmp/bot1.zip"
        with open(bot1_zip_path, "wb") as bot1_zip_file:  # todo: this can probably be done without saving to file
            bot1_zip_file.write(bot1_zip.content)
            bot1_zip_file.close()
        self.assertEqual(response.data["bot1"]["bot_zip_md5hash"], calculate_md5(bot1_zip_path))

        bot1_zip = self.client.get(response.data["bot2"]["bot_zip"])
        bot1_zip_path = "./tmp/bot2.zip"
        with open(bot1_zip_path, "wb") as bot1_zip_file:
            bot1_zip_file.write(bot1_zip.content)
            bot1_zip_file.close()
        self.assertEqual(response.data["bot2"]["bot_zip_md5hash"], calculate_md5(bot1_zip_path))

        # data
        bot1_zip = self.client.get(response.data["bot1"]["bot_data"])
        bot1_zip_path = "./tmp/bot1_data.zip"
        with open(bot1_zip_path, "wb") as bot1_zip_file:
            bot1_zip_file.write(bot1_zip.content)
            bot1_zip_file.close()
        self.assertEqual(response.data["bot1"]["bot_data_md5hash"], calculate_md5(bot1_zip_path))

        bot1_zip = self.client.get(response.data["bot2"]["bot_data"])
        bot1_zip_path = "./tmp/bot2_data.zip"
        with open(bot1_zip_path, "wb") as bot1_zip_file:
            bot1_zip_file.write(bot1_zip.content)
            bot1_zip_file.close()
        self.assertEqual(response.data["bot2"]["bot_data_md5hash"], calculate_md5(bot1_zip_path))

        # not enough available bots
        response = self._post_to_matches()
        self.assertEqual(response.status_code, 200)

        # ensure only 1 match was created
        self.assertEqual(Match.objects.count(), 1)

    def test_match_reissue(self):
        self.test_client.login(self.staffUser1)
        comp = self._create_game_mode_and_open_competition()
        self._create_map_for_competition("test_map", comp.id)

        self._create_active_bot_for_competition(comp.id, self.regularUser1, "testbot1", BotRace.terran())
        self._create_active_bot_for_competition(comp.id, self.regularUser1, "testbot2", BotRace.zerg())

        # currently we should be using arenaclientUser1's token
        response_m1 = self.test_ac_api_client.post_to_matches()
        self.assertEqual(response_m1.status_code, 201)

        # should be the same match reissued
        response_m2 = self.test_ac_api_client.post_to_matches()
        self.assertEqual(response_m2.status_code, 201)

        self.assertEqual(response_m1.data["id"], response_m2.data["id"])

    def test_match_requests_no_open_competition(self):
        """
        Tests that match requests still run when no competitions are open.
        :return:
        """

        self.test_client.login(self.staffUser1)
        game = self.test_client.create_game("StarCraft II")
        game_mode = self.test_client.create_gamemode("Melee", game.id)
        BotRace.create_all_races()
        Map.objects.create(name="testmap", game_mode=game_mode)

        bot1 = self._create_bot(self.regularUser1, "testbot1", BotRace.terran())
        self._create_bot(self.regularUser1, "testbot2", BotRace.zerg())

        # self.test_client.login(self.arenaclientUser1)

        # we shouldn't be able to get a new match
        response = self._post_to_matches()
        self.assertEqual(response.status_code, 200)
        self.assertEqual("no_game_available", response.data["detail"].code)

        Matches.request_match(self.regularUser2, bot1, bot1.get_random_excluding_self(), game_mode=game_mode)

        # now we should be able to get a match - the requested one
        response = self._post_to_matches()
        self.assertEqual(response.status_code, 201)

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
        response = self._post_to_matches()
        self.assertEqual(response.status_code, 201)
        response = self._post_to_matches()
        self.assertEqual(response.status_code, 201)
        response = self._post_to_results(response.data["id"], "Player1Win")
        self.assertEqual(response.status_code, 201)

        # Match 1 has started, Match 2 is finished.

        # Round 2
        response = self._post_to_matches()
        self.assertEqual(response.status_code, 201)
        response = self._post_to_results(response.data["id"], "Player1Win")
        self.assertEqual(response.status_code, 201)

        # Round 3 - should fail due to active round limit
        with self.assertLogs(logger="aiarena.api.arenaclient.ac_coordinator", level="DEBUG") as log:
            response = self._post_to_matches()
            self.assertEqual(response.status_code, 200)
            self.assertTrue("detail" in response.data)
            self.assertEqual("No game available for client.", response.data["detail"])
            self.assertIn(
                f"DEBUG:aiarena.api.arenaclient.ac_coordinator:Skipping competition {comp.id}: "
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
        response = self.test_ac_api_client.post_to_matches()
        self.assertEqual(response.status_code, 201)

        # we shouldn't be able to get a new match
        self.test_ac_api_client.set_api_token(Token.objects.create(user=self.arenaclientUser2).key)

        with self.assertLogs(logger="aiarena.api.arenaclient.ac_coordinator", level="DEBUG") as log:
            response = self.test_ac_api_client.post_to_matches()
            self.assertIn(
                f"DEBUG:aiarena.api.arenaclient.ac_coordinator:Skipping competition {comp.id}: "
                f"Not enough available bots for a match. Wait until more bots become available.",
                log.output,
            )

            self.assertEqual(response.status_code, 200)
            self.assertEqual("No game available for client.", response.data["detail"])

        Matches.request_match(
            self.regularUser2, bot1, bot1.get_random_active_excluding_self(), game_mode=GameMode.objects.first()
        )

        # now we should be able to get a match - the requested one
        response = self.test_ac_api_client.post_to_matches()
        self.assertEqual(response.status_code, 201)

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
        response = self._post_to_matches()
        self.assertEqual(response.status_code, 201)
        response = self._post_to_matches()
        self.assertEqual(response.status_code, 201)
        response = self._post_to_results(response.data["id"], "Player1Win")
        self.assertEqual(response.status_code, 201)

    def test_participated_in_most_recent_round(self):
        """
        Tests that the CompetitionParticipation.participated_in_most_recent_round field matches reality.
        """


class ResultsTestCase(LoggedInMixin, TransactionTestCase):
    uploaded_bot_data_path = os.path.join(BASE_DIR, PRIVATE_STORAGE_ROOT, "bots", "{0}", "bot_data")
    uploaded_bot_data_backup_path = os.path.join(BASE_DIR, PRIVATE_STORAGE_ROOT, "bots", "{0}", "bot_data_backup")
    uploaded_match_log_path = os.path.join(BASE_DIR, PRIVATE_STORAGE_ROOT, "match-logs", "{0}")
    uploaded_arenaclient_log_path = os.path.join(MEDIA_ROOT, "arenaclient-logs", "{0}_arenaclientlog.zip")

    def test_create_results(self):
        self.test_client.login(self.staffUser1)

        comp = self._create_game_mode_and_open_competition()
        self._create_map_for_competition("test_map", comp.id)

        bot1 = self._create_active_bot_for_competition(comp.id, self.regularUser1, "bot1")
        bot2 = self._create_active_bot_for_competition(comp.id, self.regularUser1, "bot2", BotRace.zerg())

        # post a standard result
        response = self._post_to_matches()
        self.assertEqual(response.status_code, 201, f"{response.status_code} {response.data}")
        match = response.data
        response = self._post_to_results(match["id"], "Player1Win")
        self.assertEqual(response.status_code, 201)

        p1 = MatchParticipation.objects.get(match_id=match["id"], participant_number=1)
        p2 = MatchParticipation.objects.get(match_id=match["id"], participant_number=2)

        # check bot datas exist
        self.assertTrue(os.path.exists(self.uploaded_bot_data_path.format(bot1.id)))
        self.assertTrue(os.path.exists(self.uploaded_bot_data_path.format(bot2.id)))

        # check hashes match set 0
        self._check_hashes(bot1, bot2, match["id"], 0)

        # check match logs exist
        self.assertTrue(os.path.exists(self.uploaded_arenaclient_log_path.format(match["id"])))
        self.assertTrue(os.path.exists(self.uploaded_match_log_path.format(p1.id)))
        self.assertTrue(os.path.exists(self.uploaded_match_log_path.format(p2.id)))

        # Post a result with different bot datas
        response = self._post_to_matches()
        self.assertEqual(response.status_code, 201)
        match = response.data
        self._post_to_results_bot_datas_set_1(match["id"], "Player1Win")
        self.assertEqual(response.status_code, 201)

        # check bot datas and their backups exist
        self.assertTrue(os.path.exists(self.uploaded_bot_data_path.format(bot1.id)))
        self.assertTrue(os.path.exists(self.uploaded_bot_data_path.format(bot2.id)))
        self.assertTrue(os.path.exists(self.uploaded_bot_data_backup_path.format(bot1.id)))
        self.assertTrue(os.path.exists(self.uploaded_bot_data_backup_path.format(bot2.id)))

        # check hashes - should be updated to set 1
        self._check_hashes(bot1, bot2, match["id"], 1)

        # check match logs exist
        self.assertTrue(os.path.exists(self.uploaded_match_log_path.format(match["id"])))
        self.assertTrue(os.path.exists(self.uploaded_match_log_path.format(p1.id)))
        self.assertTrue(os.path.exists(self.uploaded_match_log_path.format(p2.id)))

        # post a standard result with no bot1 data
        match = self._post_to_matches().data
        response = self._post_to_results_no_bot1_data(match["id"], "Player1Win", 1)
        self.assertEqual(response.status_code, 201)

        # check hashes - nothing should have changed
        self._check_hashes(bot1, bot2, match["id"], 1)

        # ensure no files got wiped
        self.assertTrue(Bot.objects.get(id=bot1.id).bot_data)
        self.assertTrue(Bot.objects.get(id=bot2.id).bot_data)

        # post a standard result with no bot2 data
        match = self._post_to_matches().data
        response = self._post_to_results_no_bot2_data(match["id"], "Player1Win", 1)
        self.assertEqual(response.status_code, 201)

        # check hashes - nothing should have changed
        self._check_hashes(bot1, bot2, match["id"], 1)

        # test that requested matches don't update bot_data
        match5 = Matches.request_match(self.staffUser1, bot1, bot2, game_mode=GameMode.objects.get())
        self._post_to_results_bot_datas_set_1(match5.id, "Player1Win")

        # check hashes - nothing should have changed
        self._check_hashes(bot1, bot2, match5.id, 1)

        # post a win without a replay - should fail
        match = self._post_to_matches().data
        response = self._post_to_results_no_replay(match["id"], "Player2Win")
        self.assertEqual(response.status_code, 400)
        self.assertTrue("non_field_errors" in response.data)
        self.assertEqual(
            response.data["non_field_errors"][0], "A win/loss or tie result must be accompanied by a replay file."
        )

        # no hashes should have changed
        self._check_hashes(bot1, bot2, match["id"], 1)

    def _check_hashes(self, bot1, bot2, match_id, data_index):
        # check hashes - nothing should have changed
        match_bot = MatchParticipation.objects.get(
            bot=bot1, match_id=match_id
        )  # use this to determine which hash to match
        if match_bot.participant_number == 1:
            self.assertEqual(
                TestAssetPaths.test_bot_datas["bot1"][data_index]["hash"], Bot.objects.get(id=bot1.id).bot_data_md5hash
            )
            self.assertEqual(
                TestAssetPaths.test_bot_datas["bot2"][data_index]["hash"], Bot.objects.get(id=bot2.id).bot_data_md5hash
            )
        else:
            self.assertEqual(
                TestAssetPaths.test_bot_datas["bot1"][data_index]["hash"], Bot.objects.get(id=bot2.id).bot_data_md5hash
            )
            self.assertEqual(
                TestAssetPaths.test_bot_datas["bot2"][data_index]["hash"], Bot.objects.get(id=bot1.id).bot_data_md5hash
            )

    def test_create_result_bot_not_in_match(self):
        self.test_client.login(self.staffUser1)

        comp = self._create_game_mode_and_open_competition()
        self._create_map_for_competition("test_map", comp.id)

        # Create 3 bots, so after a round is generated, we'll have some unstarted matches
        self._create_active_bot_for_competition(comp.id, self.regularUser1, "bot1")
        self._create_active_bot_for_competition(comp.id, self.regularUser1, "bot2", BotRace.zerg())
        self._create_active_bot_for_competition(comp.id, self.regularUser1, "bot3", BotRace.protoss())
        response = self._post_to_matches()
        self.assertEqual(response.status_code, 201, f"{response.status_code} {response.data}")

        not_started_match = Match.objects.filter(started__isnull=True, result__isnull=True).first()

        # should fail
        response = self._post_to_results(not_started_match.id, "Player1Win")
        self.assertEqual(response.status_code, 500)
        self.assertTrue("detail" in response.data)
        self.assertEqual("Unable to log result: Bot bot1 is not currently in this match!", response.data["detail"])

    def test_get_results_not_authorized(self):
        response = self.client.get("/api/arenaclient/results/")
        self.assertEqual(response.status_code, 403)

        self.client.login(username="regular_user", password="x")
        response = self.client.get("/api/arenaclient/results/")
        self.assertEqual(response.status_code, 403)

    def test_bot_crash_limit_alert(self):
        # This is the feature we're testing, so turn it on
        config.BOT_CONSECUTIVE_CRASH_LIMIT = 3

        self.test_client.login(self.staffUser1)

        comp = self._create_game_mode_and_open_competition()
        self._create_map_for_competition("test_map", comp.id)

        bot1 = self._create_active_bot_for_competition(comp.id, self.regularUser1, "bot1")
        self._create_active_bot_for_competition(comp.id, self.regularUser1, "bot2", BotRace.zerg())

        # There shouldn't yet be a crash limit alert
        self.assertTrue(BotCrashLimitAlert.objects.count() == 0)

        # log more crashes than should be allowed
        for count in range(config.BOT_CONSECUTIVE_CRASH_LIMIT):
            self._log_match_crash(bot1)

        # There should now be a single crash limit alert
        self.assertTrue(BotCrashLimitAlert.objects.count() == 1)

        # log more crashes and check it doesn't trigger an extra alert until the limit is once again reached.
        for count in range(config.BOT_CONSECUTIVE_CRASH_LIMIT - 1):
            self._log_match_crash(bot1)
        self.assertTrue(BotCrashLimitAlert.objects.count() == 1)
        self._log_match_crash(bot1)
        self.assertTrue(BotCrashLimitAlert.objects.count() == 2)

    def _log_match_crash(self, bot1):
        response = self._post_to_matches()
        self.assertEqual(response.status_code, 201, f"{response.status_code} {response.data}")
        match = response.data
        # always make the same bot crash
        if match["bot1"]["name"] == bot1.name:
            response = self._post_to_results(match["id"], "Player1Crash")
        else:
            response = self._post_to_results(match["id"], "Player2Crash")
        self.assertEqual(response.status_code, 201)

    # DISABLED UNTIL THIS FEATURE IS USED
    # def test_bot_disable_on_consecutive_crashes(self):
    #     # This is the feature we're testing, so turn it on
    #     config.BOT_CONSECUTIVE_CRASH_LIMIT = 3  # todo: this update doesn't work.
    #
    #     self.test_client.login(self.staffUser1)
    #
    #     comp = self._create_game_mode_and_open_competition()
    #     self._create_map_for_competition('test_map', comp.id)
    #
    #     bot1 = self._create_active_bot_for_competition(comp.id, self.regularUser1, 'bot1')
    #     bot2 = self._create_active_bot_for_competition(comp.id, self.regularUser1, 'bot2', BotRace.zerg())
    #
    #     # log more crashes than should be allowed
    #     for count in range(config.BOT_CONSECUTIVE_CRASH_LIMIT):
    #         response = self._post_to_matches()
    #         self.assertEqual(response.status_code, 201, f"{response.status_code} {response.data}")
    #         match = response.data
    #         # always make the same bot crash
    #         if match['bot1']['name'] == bot1.name:
    #             response = self._post_to_results(match['id'], 'Player1Crash')
    #         else:
    #             response = self._post_to_results(match['id'], 'Player2Crash')
    #         self.assertEqual(response.status_code, 201)
    #
    #     # The bot should be disabled
    #     for cp in bot1.competition_participations.all():
    #         self.assertFalse(cp.active)
    #
    #     # not enough active bots
    #     response = self._post_to_matches()
    #     self.assertEqual(response.status_code, 200)
    #     self.assertEqual(u'no_game_available', response.data['detail'].code)
    #
    #     # Post a successful match, then retry the crashes to make sure the previous ones don't affect the check
    #     cp = bot1.competition_participations.first()
    #     cp.active = True
    #     cp.save()
    #     response = self._post_to_matches()
    #     self.assertEqual(response.status_code, 201)
    #     match = response.data
    #     response = self._post_to_results(match['id'], 'Player2Win')
    #     self.assertEqual(response.status_code, 201)
    #
    #     # once again log more crashes than should be allowed
    #     for count in range(config.BOT_CONSECUTIVE_CRASH_LIMIT):
    #         response = self._post_to_matches()
    #         self.assertEqual(response.status_code, 201)
    #         match = response.data
    #         # always make the same bot crash
    #         if match['bot1']['name'] == bot1.name:
    #             response = self._post_to_results(match['id'], 'Player1Crash')
    #         else:
    #             response = self._post_to_results(match['id'], 'Player2Crash')
    #         self.assertEqual(response.status_code, 201)
    #
    #     # The bot should be disabled
    #     for cp in bot1.competition_participations.all():
    #         self.assertFalse(cp.active)
    #
    #     # not enough active bots
    #     response = self._post_to_matches()
    #     self.assertEqual(response.status_code, 200)
    #     self.assertEqual(u'no_game_available', response.data['detail'].code)


class EloTestCase(LoggedInMixin, TransactionTestCase):
    """
    Tests to ensure ELO calculations run properly.
    """

    def setUp(self):
        super(EloTestCase, self).setUp()

        self.test_client.login(self.staffUser1)

        comp = self._create_game_mode_and_open_competition()
        self._create_map_for_competition("test_map", comp.id)

        self.regularUserBot1 = self._create_bot(self.regularUser1, "regularUserBot1")
        self.regularUserBot2 = self._create_bot(self.regularUser1, "regularUserBot2")

        # self.test_client.login(self.arenaclientUser1)

        # activate the required bots
        self.regularUserBot1.competition_participations.create(competition=comp)
        self.regularUserBot2.competition_participations.create(competition=comp)

        # expected_win_sequence and expected_resultant_elos should have this many entries
        self.num_matches_to_play = 20

        self.expected_result_sequence = [
            self.regularUserBot1.id,
            self.regularUserBot2.id,
            self.regularUserBot1.id,
            self.regularUserBot1.id,
            self.regularUserBot1.id,
            "Tie",
            "Tie",
            self.regularUserBot2.id,
            "Tie",
            self.regularUserBot2.id,
            self.regularUserBot1.id,
            self.regularUserBot1.id,
            self.regularUserBot1.id,
            self.regularUserBot2.id,
            self.regularUserBot1.id,
            self.regularUserBot1.id,
            "Tie",
            self.regularUserBot1.id,
            self.regularUserBot1.id,
            self.regularUserBot1.id,
        ]

        self.expected_resultant_elos = [
            [1604, 1596],
            [1600, 1600],
            [1604, 1596],
            [1608, 1592],
            [1612, 1588],
            [1612, 1588],
            [1612, 1588],
            [1608, 1592],
            [1608, 1592],
            [1604, 1596],
            [1608, 1592],
            [1612, 1588],
            [1616, 1584],
            [1612, 1588],
            [1616, 1584],
            [1620, 1580],
            [1620, 1580],
            [1624, 1576],
            [1627, 1573],
            [1630, 1570],
        ]

    def CreateMatch(self):
        response = self._post_to_matches()
        self.assertEqual(response.status_code, 201)
        return response.data

    def CreateResult(self, match_id, r_type):
        response = self._post_to_results(match_id, r_type)
        self.assertEqual(response.status_code, 201, response.data)

    def DetermineResultType(self, bot1_id, iteration):
        if self.expected_result_sequence[iteration] == "Tie":
            return "Tie"
        else:
            return "Player1Win" if bot1_id == self.expected_result_sequence[iteration] else "Player2Win"

    def CheckResultantElos(self, match_id, iteration):
        bot1_participant = MatchParticipation.objects.filter(match_id=match_id, bot_id=self.regularUserBot1.id)[0]
        bot2_participant = MatchParticipation.objects.filter(match_id=match_id, bot_id=self.regularUserBot2.id)[0]

        self.assertEqual(self.expected_resultant_elos[iteration][0], bot1_participant.resultant_elo)
        self.assertEqual(self.expected_resultant_elos[iteration][1], bot2_participant.resultant_elo)

    def CheckFinalElos(self):
        cp1 = self.regularUserBot1.competition_participations.get()
        cp2 = self.regularUserBot2.competition_participations.get()
        self.assertEqual(cp1.elo, self.expected_resultant_elos[self.num_matches_to_play - 1][0])
        self.assertEqual(cp2.elo, self.expected_resultant_elos[self.num_matches_to_play - 1][1])

    def CheckEloSum(self):
        comp = Competition.objects.get()
        sumElo = CompetitionParticipation.objects.filter(competition=comp).aggregate(Sum("elo"))
        self.assertEqual(
            sumElo["elo__sum"], ELO_START_VALUE * Bot.objects.all().count()
        )  # starting ELO times number of bots

    def test_elo(self):
        for iteration in range(0, self.num_matches_to_play):
            match = self.CreateMatch()
            res = self.DetermineResultType(match["bot1"]["id"], iteration)
            self.CreateResult(match["id"], res)
            self.CheckResultantElos(match["id"], iteration)

        self.CheckFinalElos()

        self.CheckEloSum()

    # an exception won't be raised from this - but a log entry will
    # this is only to ensure no other exception takes place
    def test_elo_sanity_check(self):
        # todo: test log file content
        # log_file = "./logs/aiarena.log"
        # os.remove(log_file)  # clean it

        # intentionally cause a sanity check failure
        self.regularUserBot1.elo = ELO_START_VALUE - 1
        self.regularUserBot1.save()

        response = self._post_to_matches()
        self.assertEqual(response.status_code, 201)
        self._post_to_results(response.data["id"], "Player1Win")

        # with open(log_file, "r") as f:
        #     self.assertFalse("did not match expected value of" in f.read())


class RoundRobinGenerationTestCase(MatchReadyMixin, TransactionTestCase):
    def setUp(self):
        super().setUp()
        self.client.force_login(User.objects.get(username="arenaclient1"))

    def test_round_robin_generation(self):
        # avoid old tests breaking that were pre-this feature
        config.REISSUE_UNFINISHED_MATCHES = False

        # freeze every comp but one, so we can get anticipatable results
        active_comp = Competition.objects.filter(status="open").first()
        Competition.objects.exclude(id=active_comp.id).update(status="frozen")

        # we need to deactivate a bot midway through the test, so we'll activate this one for now
        bot_to_deactivate = CompetitionParticipation.objects.create(
            bot_id=self.regularUser1Bot3_Inactive.id, competition_id=active_comp.id
        )
        bot_to_deactivate.active = True
        bot_to_deactivate.save()

        bot_count = CompetitionParticipation.objects.filter(active=True, competition=active_comp).count()
        bot_count_after_deactivation = bot_count - 1
        expected_matches = lambda bc: int(bc / 2 * (bc - 1))
        expected_match_count_per_round = expected_matches(bot_count)
        expected_match_count_per_round_after_bot_deactivated = expected_matches(bot_count_after_deactivation)
        self.assertGreater(bot_count, 1)  # check we have more than 1 bot

        self.assertEqual(Match.objects.count(), 0)  # starting with 0 matches
        self.assertEqual(Round.objects.count(), 0)  # starting with 0 rounds

        # Validate that participated_in_most_recent_round flags have not been set yet
        self.assertTrue(
            CompetitionParticipation.objects.filter(
                competition=active_comp, participated_in_most_recent_round=True
            ).count()
            == 0
        )

        response = self._post_to_matches()  # this should trigger a new round robin generation
        self.assertEqual(response.status_code, 201)

        # Validate that participated_in_most_recent_round flags have now been set
        self.assertTrue(
            CompetitionParticipation.objects.filter(
                competition=active_comp, participated_in_most_recent_round=True
            ).count()
            == bot_count
        )

        # check match count
        self.assertEqual(Match.objects.count(), expected_match_count_per_round)

        # check round data
        self.assertEqual(Round.objects.count(), 1)
        round1 = Round.objects.get()  # get the only round
        self.assertIsNotNone(round1.started)
        self.assertIsNone(round1.finished)
        self.assertFalse(round1.complete)

        # finish the initial match
        response = self._post_to_results(response.data["id"], "Player1Win")
        self.assertEqual(response.status_code, 201)

        # start and finish all the rest of the generated matches
        for x in range(1, expected_match_count_per_round):
            response = self._post_to_matches()
            self.assertEqual(response.status_code, 201)
            response = self._post_to_results(response.data["id"], "Player1Win")
            self.assertEqual(response.status_code, 201)
            # double check the match count
            self.assertEqual(Match.objects.filter(started__isnull=True).count(), expected_match_count_per_round - x - 1)

        # check round is finished
        self.assertEqual(Round.objects.count(), 1)
        round1.refresh_from_db()
        self.assertIsNotNone(round1.finished)
        self.assertTrue(round1.complete)

        # Repeat again but with quirks

        response = self._post_to_matches()  # this should trigger another new round robin generation
        self.assertEqual(response.status_code, 201)

        # Validate that participated_in_most_recent_round flags are still set properly
        self.assertTrue(
            CompetitionParticipation.objects.filter(
                competition=active_comp, participated_in_most_recent_round=True
            ).count()
            == bot_count
        )

        # check match count
        self.assertEqual(Match.objects.count(), expected_match_count_per_round * 2)

        # check round data
        self.assertEqual(Round.objects.count(), 2)
        round2 = Round.objects.get(id=round1.id + 1)
        self.assertIsNotNone(round2.started)
        self.assertIsNone(round2.finished)
        self.assertFalse(round2.complete)

        # finish the initial match
        response = self._post_to_results(response.data["id"], "Player1Win")
        self.assertEqual(response.status_code, 201)

        # start and finish all except one the rest of the generated matches
        for x in range(1, expected_match_count_per_round - 1):
            response = self._post_to_matches()
            self.assertEqual(response.status_code, 201)
            response = self._post_to_results(response.data["id"], "Player1Win")
            self.assertEqual(response.status_code, 201)
            # double check the match count
            self.assertEqual(Match.objects.filter(started__isnull=True).count(), expected_match_count_per_round - x - 1)

        # at this stage there should be one unstarted match left
        self.assertEqual(Match.objects.filter(started__isnull=True).count(), 1)

        # start the last match
        response2ndRoundLastMatch = self._post_to_matches()
        self.assertEqual(response2ndRoundLastMatch.status_code, 201)
        self.assertEqual(Match.objects.filter(started__isnull=True).count(), 0)

        # deactivate a bot so that we can check it's participated_in_most_recent_round field is updated appropriately
        bot_to_deactivate.active = False
        bot_to_deactivate.save()

        # the following part ensures round generation is properly handled when an old round is not yet finished
        response = self._post_to_matches()
        self.assertEqual(response.status_code, 201)

        # Validate that participated_in_most_recent_round flags reflect the deactivated bot
        self.assertTrue(
            CompetitionParticipation.objects.filter(
                competition=active_comp, participated_in_most_recent_round=True
            ).count()
            == bot_count - 1
        )
        bot_to_deactivate.refresh_from_db()
        self.assertFalse(bot_to_deactivate.participated_in_most_recent_round)

        self.assertEqual(
            Match.objects.filter(started__isnull=True).count(), expected_match_count_per_round_after_bot_deactivated - 1
        )
        total_expected_match_count = (
            expected_match_count_per_round * 2
        ) + expected_match_count_per_round_after_bot_deactivated
        self.assertEqual(Match.objects.count(), total_expected_match_count)

        # check round data
        self.assertEqual(Round.objects.count(), 3)

        # check 2nd round data is still the same
        round2.refresh_from_db()
        self.assertIsNotNone(round2.started)
        self.assertIsNone(round2.finished)
        self.assertFalse(round2.complete)

        # check 3rd round data
        round3 = Round.objects.get(id=round2.id + 1)
        self.assertIsNotNone(round3.started)
        self.assertIsNone(round3.finished)
        self.assertFalse(round3.complete)

        # now finish the 2nd round
        response = self._post_to_results(response2ndRoundLastMatch.data["id"], "Player1Win")
        self.assertEqual(response.status_code, 201)

        # check round is finished
        round2.refresh_from_db()
        self.assertIsNotNone(round2.finished)
        self.assertTrue(round2.complete)

        # check 3rd round data remains unmodified
        round3.refresh_from_db()
        self.assertIsNotNone(round3.started)
        self.assertIsNone(round3.finished)
        self.assertFalse(round3.complete)

        # check result count - should have 2 rounds worth of results
        self.assertEqual(Result.objects.count(), expected_match_count_per_round * 2)


class CompetitionsDivisionsTestCase(MatchReadyMixin, TransactionTestCase):
    """
    Test competition divisions
    """

    def setUp(self):
        super().setUp()
        self._generate_extra_users()
        self._generate_extra_bots()
        self.client.force_login(User.objects.get(username="arenaclient1"))

    def test_split_merge_logic(self):
        def _check(competition, n_bots, split_points, merge_points):
            # Add bots to competition
            for i in range(n_bots):
                if i in split_points:
                    self.assertEqual(competition.should_split_divisions(i), True)
                    competition.n_divisions += 1
                else:
                    self.assertEqual(competition.should_split_divisions(i), False)
            # Remove bots from competition
            competition.n_divisions = competition.target_n_divisions
            for i in range(n_bots, 0, -1):
                if i in merge_points:
                    self.assertEqual(competition.should_merge_divisions(i), True)
                    competition.n_divisions -= 1
                else:
                    self.assertEqual(competition.should_merge_divisions(i), False)

        competition = self._create_open_competition(GameMode.objects.first().id, "Split/Merge Test Competition")
        # By default there should be no splitting happening
        _check(competition, 50, [], [])
        # 2 divisions
        competition.target_n_divisions = 2
        competition.n_divisions = 1
        competition.target_division_size = 15
        _check(competition, 100, [30], [22])
        # 3 divisions
        competition.target_n_divisions = 3
        competition.n_divisions = 1
        competition.target_division_size = 8
        _check(competition, 50, [16, 24], [12, 20])
        # small divisions
        competition.target_n_divisions = 5
        competition.n_divisions = 1
        competition.target_division_size = 2
        _check(competition, 20, [4, 6, 8, 10], [3, 5, 7, 9])
        # small divisions
        competition.target_n_divisions = 4
        competition.n_divisions = 1
        competition.target_division_size = 3
        _check(competition, 30, [6, 9, 12], [4, 7, 10])

    def _get_div_participant_count(self, competition):
        div_participants = dict()
        current_elo = -1
        current_div = competition.target_n_divisions
        current_in_placements = True
        existing_participants = (
            CompetitionParticipation.objects.filter(
                active=True,
                competition=competition,
                in_placements=False,
                division_num__gte=CompetitionParticipation.MIN_DIVISION,
            )
            .only("division_num", "elo", "match_count", "in_placements")
            .order_by("-division_num", "elo")
        )
        placement_participants = (
            CompetitionParticipation.objects.filter(
                active=True,
                competition=competition,
                in_placements=True,
                division_num__gte=CompetitionParticipation.MIN_DIVISION,
            )
            .only("division_num", "elo", "match_count", "in_placements")
            .order_by("-division_num", "match_count", "elo")
        )
        for cp in list(placement_participants) + list(existing_participants):
            if cp.in_placements:
                self.assertEqual(current_in_placements, True)  # Preceding bot should be in placement
                # TODO: This was commented out to make this test pass as it broke when the stats update was added
                # TODO: to the result submission. Prior to this point, cp.match_count was always 0 because it's only
                # TODO: filled in when the stats gen is run.
                # TODO: What is this check supposed to do?
                # self.assertGreaterEqual(cp.match_count, current_match_count) # Asc match count
                if competition.n_placements > 0 and competition.rounds_this_cycle == 1:
                    self.assertLess(
                        cp.match_count, competition.n_placements
                    )  # Should have less matches played than placement reqs
            else:
                if not current_in_placements and competition.rounds_this_cycle == 1:
                    self.assertGreaterEqual(cp.elo, current_elo)  # Asc ELO
                self.assertGreaterEqual(
                    cp.match_count, competition.n_placements
                )  # Should have at least equal matches played than placement reqs
            self.assertLessEqual(cp.division_num, current_div)  # Desc Div nums
            current_in_placements = cp.in_placements
            current_elo = cp.elo
            current_div = cp.division_num
            if cp.division_num in div_participants:
                div_participants[cp.division_num]["n"] += 1
                div_participants[cp.division_num]["p"] += 1 if cp.in_placements else 0
            else:
                div_participants[cp.division_num] = {"n": 1, "p": 1 if cp.in_placements else 0}
        return div_participants

    def _get_expected_matches_per_div(self, round):
        matches_per_div = dict()
        for m in Match.objects.filter(round=round):
            div = m.participant1.competition_participant.division_num
            self.assertEqual(div, m.participant2.competition_participant.division_num)
            if div in matches_per_div:
                matches_per_div[div] += 1
            else:
                matches_per_div[div] = 1
        return matches_per_div

    def _complete_round(self, competition, exp_round, exp_div_participant_count, exp_n_matches):
        # this should trigger a new round
        response = self._post_to_matches()
        self.assertEqual(response.status_code, 201)
        # check round data
        round = Round.objects.filter(competition=competition).order_by("-number").first()
        self.assertEqual(round.number, exp_round)
        self.assertIsNotNone(round.started)
        self.assertIsNone(round.finished)
        self.assertFalse(round.complete)
        # check match count, also checks divisions are in elo order
        competition.refresh_from_db()
        self.assertEqual(self._get_div_participant_count(competition), exp_div_participant_count)
        exp_matches_per_div = self._get_expected_matches_per_div(round)
        self.assertEqual(exp_matches_per_div, exp_n_matches)
        total_exp_matches_per_div = sum(exp_matches_per_div.values())
        self.assertEqual(Match.objects.filter(round=round).count(), total_exp_matches_per_div)
        # finish the initial match
        response = self._post_to_results(response.data["id"], "Player1Win")
        self.assertEqual(response.status_code, 201)

        # start and finish all the rest of the generated matches
        for x in range(1, total_exp_matches_per_div):
            response = self._post_to_matches()
            self.assertEqual(response.status_code, 201)
            response = self._post_to_results(response.data["id"], "Player1Win")
            self.assertEqual(response.status_code, 201)
            # double check the match count
            self.assertEqual(Match.objects.filter(started__isnull=True).count(), total_exp_matches_per_div - x - 1)

        # check round is finished
        round = Round.objects.filter(competition=competition).order_by("-number").first()
        self.assertEqual(round.number, exp_round)
        self.assertIsNotNone(round.finished)
        self.assertTrue(round.complete)

    def _complete_cycle(self, competition, exp_rounds, exp_div_participant_count, exp_n_matches):
        for i in range(competition.rounds_per_cycle):
            self._complete_round(competition, exp_rounds[i], exp_div_participant_count, exp_n_matches)
            self.assertEqual(competition.rounds_this_cycle, i + 1)

    def _set_up_competition(self, target_divs, div_size, rpc=1, n_placements=0):
        # avoid old tests breaking that were pre-this feature
        config.REISSUE_UNFINISHED_MATCHES = False

        # freeze every comp but one, so we can get anticipatable results
        competition = self._create_open_competition(GameMode.objects.first().id, "Test Competition")
        # Set up division settings
        competition.target_n_divisions = target_divs
        competition.target_division_size = div_size
        competition.n_placements = n_placements
        competition.rounds_per_cycle = rpc
        competition.save()
        Competition.objects.exclude(id=competition.id).update(status="frozen")
        self._create_map_for_competition("testmapdiv1", competition.id)
        self.assertEqual(Match.objects.count(), 0)  # starting with 0 matches
        self.assertEqual(Round.objects.count(), 0)  # starting with 0 rounds
        return competition

    def test_placements_enabled(self):
        competition = self._set_up_competition(3, 3, 2, 6)
        _exp_par = lambda x, y: {"n": x, "p": y}
        CompetitionParticipation.objects.create(bot_id=self.regularUser1Bot1.id, competition_id=competition.id)
        CompetitionParticipation.objects.create(bot_id=self.staffUser1Bot1.id, competition_id=competition.id)
        self._complete_cycle(competition, [1, 2], {1: _exp_par(2, 2)}, {1: 1})
        CompetitionParticipation.objects.create(bot_id=self.regularUser1Bot2.id, competition_id=competition.id)
        self._complete_cycle(competition, [3, 4], {1: _exp_par(3, 3)}, {1: 3})
        self._complete_cycle(competition, [5, 6], {1: _exp_par(3, 1)}, {1: 3})
        CompetitionParticipation.objects.create(bot_id=self.staffUser1Bot2.id, competition_id=competition.id)
        CompetitionParticipation.objects.create(bot_id=self.regularUser1Bot3_Inactive.id, competition_id=competition.id)
        CompetitionParticipation.objects.create(bot_id=self.staffUser1Bot3.id, competition_id=competition.id)
        CompetitionParticipation.objects.create(bot_id=self.regularUser1Bot4.id, competition_id=competition.id)
        CompetitionParticipation.objects.create(bot_id=self.regularUser2Bot1.id, competition_id=competition.id)
        CompetitionParticipation.objects.create(bot_id=self.regularUser2Bot2.id, competition_id=competition.id)
        CompetitionParticipation.objects.create(bot_id=self.regularUser3Bot1.id, competition_id=competition.id)
        CompetitionParticipation.objects.create(bot_id=self.regularUser3Bot2.id, competition_id=competition.id)
        CompetitionParticipation.objects.create(bot_id=self.regularUser4Bot1.id, competition_id=competition.id)
        CompetitionParticipation.objects.create(bot_id=self.regularUser4Bot2.id, competition_id=competition.id)
        for j in range(3):
            u = User.objects.create_user(
                username=f"regular_user{100+j}", password="x", email=f"regular_user{100+j}@dev.aiarena.net"
            )
            for i in range(3):
                self._create_active_bot_for_competition(competition.id, u, f"{u.username}Bot{i+1}")
        self._complete_cycle(
            competition, [7, 8], {1: _exp_par(7, 4), 2: _exp_par(7, 7), 3: _exp_par(8, 8)}, {1: 21, 2: 21, 3: 28}
        )
        self._complete_cycle(
            competition, [9, 10], {1: _exp_par(7, 0), 2: _exp_par(7, 0), 3: _exp_par(8, 0)}, {1: 21, 2: 21, 3: 28}
        )

    def test_first_round_no_split(self):
        competition = self._set_up_competition(2, 2, 5)
        _exp_par = lambda x, y: {"n": x, "p": y}
        CompetitionParticipation.objects.create(bot_id=self.staffUser1Bot2.id, competition_id=competition.id)
        CompetitionParticipation.objects.create(bot_id=self.regularUser1Bot3_Inactive.id, competition_id=competition.id)
        CompetitionParticipation.objects.create(bot_id=self.staffUser1Bot3.id, competition_id=competition.id)
        CompetitionParticipation.objects.create(bot_id=self.regularUser1Bot4.id, competition_id=competition.id)
        CompetitionParticipation.objects.create(bot_id=self.regularUser2Bot1.id, competition_id=competition.id)
        CompetitionParticipation.objects.create(bot_id=self.regularUser2Bot2.id, competition_id=competition.id)
        CompetitionParticipation.objects.create(bot_id=self.regularUser3Bot1.id, competition_id=competition.id)
        CompetitionParticipation.objects.create(bot_id=self.regularUser3Bot2.id, competition_id=competition.id)
        CompetitionParticipation.objects.create(bot_id=self.regularUser4Bot1.id, competition_id=competition.id)
        CompetitionParticipation.objects.create(bot_id=self.regularUser4Bot2.id, competition_id=competition.id)
        self._complete_cycle(competition, [1, 2, 3, 4, 5], {1: _exp_par(10, 0)}, {1: 45})
        self._complete_cycle(competition, [6, 7, 8, 9, 10], {1: _exp_par(5, 0), 2: _exp_par(5, 0)}, {1: 10, 2: 10})

    def test_no_insertions_mid_cycle(self):
        # And also no matches between those without divisions
        competition = self._set_up_competition(2, 4, 3)
        _exp_par = lambda x, y: {"n": x, "p": y}

        CompetitionParticipation.objects.create(bot_id=self.staffUser1Bot2.id, competition_id=competition.id)
        CompetitionParticipation.objects.create(bot_id=self.regularUser1Bot3_Inactive.id, competition_id=competition.id)
        self._complete_round(competition, 1, {1: _exp_par(2, 0)}, {1: 1})
        CompetitionParticipation.objects.create(bot_id=self.staffUser1Bot3.id, competition_id=competition.id)
        self._complete_round(competition, 2, {1: _exp_par(2, 0)}, {1: 1})
        CompetitionParticipation.objects.create(bot_id=self.regularUser1Bot4.id, competition_id=competition.id)
        self._complete_round(competition, 3, {1: _exp_par(2, 0)}, {1: 1})
        self._complete_round(competition, 4, {1: _exp_par(4, 0)}, {1: 6})

    def test_division_matchmaking(self):
        competition = self._set_up_competition(3, 3, 3)

        _exp_par = lambda x: {"n": x, "p": 0}
        # Start Rounds
        CompetitionParticipation.objects.create(bot_id=self.regularUser1Bot1.id, competition_id=competition.id)
        CompetitionParticipation.objects.create(bot_id=self.staffUser1Bot1.id, competition_id=competition.id)
        self._complete_cycle(competition, [1, 2, 3], {1: _exp_par(2)}, {1: 1})
        CompetitionParticipation.objects.create(bot_id=self.regularUser1Bot2.id, competition_id=competition.id)
        CompetitionParticipation.objects.create(bot_id=self.staffUser1Bot2.id, competition_id=competition.id)
        self._complete_cycle(competition, [4, 5, 6], {1: _exp_par(4)}, {1: 6})
        # Split to 2 divs
        self.ru1b3_cp = CompetitionParticipation.objects.create(
            bot_id=self.regularUser1Bot3_Inactive.id, competition_id=competition.id
        )
        self.su1b3_cp = CompetitionParticipation.objects.create(
            bot_id=self.staffUser1Bot3.id, competition_id=competition.id
        )
        self._complete_cycle(competition, [7, 8, 9], {1: _exp_par(3), 2: _exp_par(3)}, {1: 3, 2: 3})
        # Bot inactive dont merge yet
        self.ru1b3_cp.active = False
        self.ru1b3_cp.save()
        self._complete_cycle(competition, [10, 11, 12], {1: _exp_par(2), 2: _exp_par(3)}, {1: 1, 2: 3})
        # Merge threshold reached
        self.su1b3_cp.active = False
        self.su1b3_cp.save()
        self._complete_cycle(competition, [13, 14, 15], {1: _exp_par(4)}, {1: 6})
        # Non equal divisions
        self.ru1b3_cp.active = True
        self.ru1b3_cp.save()
        self.su1b3_cp.active = True
        self.su1b3_cp.save()
        self.ru1b4_cp = CompetitionParticipation.objects.create(
            bot_id=self.regularUser1Bot4.id, competition_id=competition.id
        )
        self._complete_cycle(competition, [16, 17, 18], {1: _exp_par(3), 2: _exp_par(4)}, {1: 3, 2: 6})
        # Split to 3 divs
        self.ru2b1_cp = CompetitionParticipation.objects.create(
            bot_id=self.regularUser2Bot1.id, competition_id=competition.id
        )
        self.ru2b2_cp = CompetitionParticipation.objects.create(
            bot_id=self.regularUser2Bot2.id, competition_id=competition.id
        )
        self._complete_cycle(
            competition, [19, 20, 21], {1: _exp_par(3), 2: _exp_par(3), 3: _exp_par(3)}, {1: 3, 2: 3, 3: 3}
        )
        # Merge again
        self.ru1b3_cp.active = False
        self.ru1b3_cp.save()
        self._complete_cycle(
            competition, [22, 23, 24], {1: _exp_par(2), 2: _exp_par(3), 3: _exp_par(3)}, {1: 1, 2: 3, 3: 3}
        )
        self.su1b3_cp.active = False
        self.su1b3_cp.save()
        self._complete_cycle(competition, [25, 26, 27], {1: _exp_par(3), 2: _exp_par(4)}, {1: 3, 2: 6})
        self.ru2b1_cp.active = False
        self.ru2b1_cp.save()
        self._complete_cycle(competition, [28, 29, 30], {1: _exp_par(3), 2: _exp_par(3)}, {1: 3, 2: 3})
        self.ru1b3_cp.active = True
        self.ru1b3_cp.save()
        self.su1b3_cp.active = True
        self.su1b3_cp.save()
        self.ru2b1_cp.active = True
        self.ru2b1_cp.save()
        self._complete_cycle(
            competition, [31, 32, 33], {1: _exp_par(3), 2: _exp_par(3), 3: _exp_par(3)}, {1: 3, 2: 3, 3: 3}
        )
        # Grow equally
        CompetitionParticipation.objects.create(bot_id=self.regularUser3Bot1.id, competition_id=competition.id)
        CompetitionParticipation.objects.create(bot_id=self.regularUser3Bot2.id, competition_id=competition.id)
        CompetitionParticipation.objects.create(bot_id=self.regularUser4Bot1.id, competition_id=competition.id)
        CompetitionParticipation.objects.create(bot_id=self.regularUser4Bot2.id, competition_id=competition.id)
        self._complete_cycle(
            competition, [34, 35, 36], {1: _exp_par(4), 2: _exp_par(4), 3: _exp_par(5)}, {1: 6, 2: 6, 3: 10}
        )
        self._create_active_bot_for_competition(competition.id, self.regularUser2, "regularUser2Bot100")
        self._complete_cycle(
            competition, [37, 38, 39], {1: _exp_par(4), 2: _exp_par(5), 3: _exp_par(5)}, {1: 6, 2: 10, 3: 10}
        )
        # Not more splits
        for j in range(3):
            u = User.objects.create_user(
                username=f"regular_user{100+j}", password="x", email=f"regular_user{100+j}@dev.aiarena.net"
            )
            for i in range(3):
                self._create_active_bot_for_competition(competition.id, u, f"{u.username}Bot{i+1}")
        self._complete_cycle(
            competition, [40, 41, 42], {1: _exp_par(7), 2: _exp_par(8), 3: _exp_par(8)}, {1: 21, 2: 28, 3: 28}
        )


class SetStatusTestCase(LoggedInMixin, TransactionTestCase):
    def setUp(self):
        super().setUp()
        self.client.force_login(User.objects.get(username="arenaclient1"))

    def test_set_status(self):
        return self.client.post("/api/arenaclient/set-status/", {"status": "idle"})


class ArenaClientCompatibilityTestCase(MatchReadyMixin, TransactionTestCase):
    """
    This test ensures that the Arena Client endpoint doesn't inadvertently change.

    IF THIS TEST FAILS, YOU MIGHT HAVE BROKEN COMPATIBILITY WITH THE ARENA CLIENT
    """

    def setUp(self):
        super().setUp()
        self.client.force_login(User.objects.get(username="arenaclient1"))

    def validateJson_bySchema(self, jsonData, json_schema) -> (bool, jsonschema.exceptions.ValidationError):
        try:
            jsonschema.validate(instance=jsonData, schema=json_schema)
        except jsonschema.exceptions.ValidationError as error:
            return False, error
        return True, None

    def test_endpoint_contract(self):
        response = self._post_to_matches()
        self.assertEqual(response.status_code, 201)
        json_schema = {
            "type": "object",
            "additionalProperties": False,
            "required": ["id"],
            "properties": {
                "id": {"type": "number"},
                "bot1": {
                    "type": "object",
                    "additionalProperties": False,
                    "required": [
                        "id",
                        "name",
                        "game_display_id",
                        "bot_zip",
                        "bot_zip_md5hash",
                        "bot_data",
                        "bot_data_md5hash",
                        "plays_race",
                        "type",
                    ],
                    "properties": {
                        "id": {"type": "number"},
                        "name": {"type": "string"},
                        "game_display_id": {"type": "string"},
                        "bot_zip": {"type": "string"},
                        "bot_zip_md5hash": {"type": "string"},
                        "bot_data": {"type": "string"},
                        "bot_data_md5hash": {"type": "string"},
                        "plays_race": {"type": "string"},
                        "type": {"type": "string"},
                    },
                },
                "bot2": {
                    "type": "object",
                    "additionalProperties": False,
                    "required": [
                        "id",
                        "name",
                        "game_display_id",
                        "bot_zip",
                        "bot_zip_md5hash",
                        "bot_data",
                        "bot_data_md5hash",
                        "plays_race",
                        "type",
                    ],
                    "properties": {
                        "id": {"type": "number"},
                        "name": {"type": "string"},
                        "game_display_id": {"type": "string"},
                        "bot_zip": {"type": "string"},
                        "bot_zip_md5hash": {"type": "string"},
                        "bot_data": {"type": "string"},
                        "bot_data_md5hash": {"type": "string"},
                        "plays_race": {"type": "string"},
                        "type": {"type": "string"},
                    },
                },
                "map": {
                    "type": "object",
                    "additionalProperties": False,
                    "required": ["id", "name", "file", "enabled", "game_mode", "competitions"],
                    "properties": {
                        "id": {"type": "number"},
                        "name": {"type": "string"},
                        "file": {"type": "string"},
                        "enabled": {"type": "boolean"},
                        "game_mode": {"type": "number"},
                        "competitions": {"type": "array"},
                    },
                },
            },
        }

        validation_successful, error = self.validateJson_bySchema(json.load(io.BytesIO(response.content)), json_schema)
        if not validation_successful:
            raise Exception(
                "The AC API next match endpoint json schema has changed! "
                "If you intentionally changed it, update this test and the arenaclient.\n"
                "ValidationError:\n" + str(error)
            )
