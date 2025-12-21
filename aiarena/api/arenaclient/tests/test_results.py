from django.test import TransactionTestCase

from constance import config

from aiarena.core.models import Bot, BotCrashLimitAlert, GameMode, Match, MatchParticipation
from aiarena.core.models.bot_race import BotRace
from aiarena.core.services import match_requests
from aiarena.core.tests.test_mixins import LoggedInMixin
from aiarena.core.tests.testing_utils import TestAssetPaths


class ResultsTestCase(LoggedInMixin, TransactionTestCase):
    def test_create_results(self):
        self.test_client.login(self.staffUser1)

        comp = self._create_game_mode_and_open_competition()
        self._create_map_for_competition("test_map", comp.id)

        bot1 = self._create_active_bot_for_competition(comp.id, self.regularUser1, "bot1")
        bot2 = self._create_active_bot_for_competition(comp.id, self.regularUser1, "bot2", BotRace.zerg())

        # post a standard result
        response = self._post_to_matches()
        match = response.data
        self._post_to_results(match["id"], "Player1Win")

        MatchParticipation.objects.get(match_id=match["id"], participant_number=1)
        MatchParticipation.objects.get(match_id=match["id"], participant_number=2)

        # check hashes match set 0
        self._check_hashes(bot1, bot2, match["id"], 0)

        # Post a result with different bot datas
        response = self._post_to_matches()
        match = response.data
        self._post_to_results_bot_datas_set_1(match["id"], "Player1Win")

        # check hashes - should be updated to set 1
        self._check_hashes(bot1, bot2, match["id"], 1)

        # post a standard result with no bot1 data
        match = self._post_to_matches().data
        response = self._post_to_results_no_bot1_data(match["id"], "Player1Win", 1)

        # check hashes - nothing should have changed
        self._check_hashes(bot1, bot2, match["id"], 1)

        # ensure no files got wiped
        self.assertTrue(Bot.objects.get(id=bot1.id).bot_data)
        self.assertTrue(Bot.objects.get(id=bot2.id).bot_data)

        # post a standard result with no bot2 data
        match_id = self._post_to_matches().data["id"]
        self._post_to_results_no_bot2_data(match_id, "Player1Win", 1)

        # check hashes - nothing should have changed
        self._check_hashes(bot1, bot2, match["id"], 1)

        # test that requested matches don't update bot_data
        requested_match = match_requests.request_match(self.staffUser1, bot1, bot2, game_mode=GameMode.objects.get())
        match_id = self._post_to_matches().data["id"]
        assert match_id == requested_match.id
        self._post_to_results_bot_datas_set_1(requested_match.id, "Player1Win")

        # check hashes - nothing should have changed
        self._check_hashes(bot1, bot2, requested_match.id, 1)

        # post a win without a replay - should fail
        match_id = self._post_to_matches().data["id"]
        response = self._post_to_results_no_replay(match_id, "Player2Win", expected_code=400)
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
        self._post_to_matches()

        not_started_match = Match.objects.filter(started__isnull=True, result__isnull=True).first()

        # should fail
        response = self._post_to_results(not_started_match.id, "Player1Win", expected_code=500)
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
        match = self._post_to_matches().data
        # always make the same bot crash
        if match["bot1"]["name"] == bot1.name:
            self._post_to_results(match["id"], "Player1Crash")
        else:
            self._post_to_results(match["id"], "Player2Crash")

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
