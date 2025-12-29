import os
from unittest import TestCase

from django.core.files import File
from django.core.files.uploadedfile import SimpleUploadedFile

from constance import config
from rest_framework.authtoken.models import Token

from aiarena import settings
from aiarena.api.arenaclient.testing_utils import AcApiTestingClient
from aiarena.core.models import (
    ArenaClient,
    Bot,
    Competition,
    CompetitionParticipation,
    GameMode,
    Map,
    MapPool,
    User,
    WebsiteUser,
)
from aiarena.core.models.bot_race import BotRace
from aiarena.core.services import match_requests
from aiarena.core.tests.testing_utils import TestAssetPaths


class BaseTestMixin(TestCase):
    """
    Base test case for testing. Contains references to all the test files such as test bot zips etc.
    """

    def setUp(self):
        from aiarena.core.tests.testing_utils import TestingClient  # avoid circular import

        self.test_client = TestingClient(self.client)
        self.test_ac_api_client = AcApiTestingClient()

    def _create_map_for_competition(self, name, competition_id):
        with open(TestAssetPaths.test_map_path, "rb") as map_file:
            competition = Competition.objects.get(id=competition_id)
            map = Map.objects.create(name=name, game_mode=competition.game_mode, file=File(map_file))
            map.competitions.add(competition)
            return map

    def _create_map_for_game_mode(self, name, game_mode_id):
        map = Map.objects.create(name=name, game_mode_id=game_mode_id)
        return map

    def _create_competition(self, gamemode_id: int, name="Competition 1", playable_race_ids=None):
        competition = Competition.objects.create(name=name, game_mode_id=gamemode_id)
        if playable_race_ids:
            for race_id in playable_race_ids:
                competition.playable_races.add(race_id)
        return competition

    def _create_open_competition(self, gamemode_id: int, name="Competition 1", playable_race_ids=None):
        competition = self._create_competition(gamemode_id, name, playable_race_ids)
        competition.open()
        return competition

    def _create_game_mode_and_open_competition(self, trusted=True):
        game = self.test_client.create_game("StarCraft II", ".SC2Map")
        gamde_mode = self.test_client.create_gamemode("Melee", game.id)
        BotRace.create_all_races()
        competition = self.test_client.create_competition(
            "Competition 1", gamde_mode.id, require_trusted_infrastructure=trusted
        )
        self.test_client.open_competition(competition.id)
        return competition

    def _create_bot(self, user, name, plays_race=None):
        if plays_race is None:
            plays_race = BotRace.terran()
        with (
            open(TestAssetPaths.test_bot_zip_path, "rb") as bot_zip,
            open(TestAssetPaths.test_bot_datas["bot1"][0]["path"], "rb") as bot_data,
        ):
            bot = Bot(
                user=user,
                name=name,
                bot_zip=File(bot_zip),
                bot_data=File(bot_data),
                plays_race=plays_race,
                type="python",
            )
            bot.full_clean()
            bot.save()
            return bot

    def _create_active_bot_for_competition(self, competition_id: int, user, name, plays_race=None, downloadable=False):
        if plays_race is None:
            plays_race = BotRace.terran()
        with (
            open(TestAssetPaths.test_bot_zip_path, "rb") as bot_zip,
            open(TestAssetPaths.test_bot_datas["bot1"][0]["path"], "rb") as bot_data,
        ):
            bot = Bot(
                user=user,
                name=name,
                bot_zip=File(bot_zip),
                bot_data=File(bot_data),
                plays_race=plays_race,
                type="python",
                bot_zip_publicly_downloadable=downloadable,
                bot_data_publicly_downloadable=downloadable,
            )
            bot.full_clean()
            bot.save()
            CompetitionParticipation.objects.create(bot_id=bot.id, competition_id=competition_id)
            return bot

    def _post_to_matches(self, api_version=None, expected_code=201):
        if api_version:
            self.test_ac_api_client.set_api_version(api_version)
        return self.test_ac_api_client.post_to_matches(expected_code=expected_code)

    def _post_to_results(self, match_id, result_type, bot1_tags=None, bot2_tags=None, expected_code=201):
        """
        Posts a generic result.
        :param match_id:
        :param result_type:
        :return:
        """
        filename = os.path.join(
            os.path.dirname(os.path.realpath(__file__)), "test-media/../test-media/testReplay.SC2Replay"
        )
        with (
            open(filename, "rb") as replay_file,
            open(TestAssetPaths.test_bot_datas["bot1"][0]["path"], "rb") as bot1_data,
            open(TestAssetPaths.test_bot_datas["bot2"][0]["path"], "rb") as bot2_data,
            open(TestAssetPaths.test_bot1_match_log_path, "rb") as bot1_log,
            open(TestAssetPaths.test_bot2_match_log_path, "rb") as bot2_log,
            open(TestAssetPaths.test_arenaclient_log_path, "rb") as arenaclient_log,
        ):
            return self.test_ac_api_client.submit_custom_result(
                match_id,
                result_type,
                replay_file,
                bot1_data,
                bot2_data,
                bot1_log,
                bot2_log,
                arenaclient_log,
                bot1_tags,
                bot2_tags,
                expected_code=expected_code,
            )

    def _post_to_results_bot_datas_set_1(self, match_id, result_type, expected_code=201):
        """
        Posts a generic result, using bot datas of index 1.
        :param match_id:
        :param result_type:
        :return:
        """
        filename = os.path.join(
            os.path.dirname(os.path.realpath(__file__)), "test-media/../test-media/testReplay.SC2Replay"
        )
        with (
            open(filename, "rb") as replay_file,
            open(TestAssetPaths.test_bot_datas["bot1"][1]["path"], "rb") as bot1_data,
            open(TestAssetPaths.test_bot_datas["bot2"][1]["path"], "rb") as bot2_data,
            open(TestAssetPaths.test_bot1_match_log_path, "rb") as bot1_log,
            open(TestAssetPaths.test_bot2_match_log_path, "rb") as bot2_log,
            open(TestAssetPaths.test_arenaclient_log_path, "rb") as arenaclient_log,
        ):
            return self.test_ac_api_client.submit_custom_result(
                match_id,
                result_type,
                replay_file,
                bot1_data,
                bot2_data,
                bot1_log,
                bot2_log,
                arenaclient_log,
                expected_code=expected_code,
            )

    def _post_to_results_no_bot_datas(self, match_id, result_type):
        filename = os.path.join(
            os.path.dirname(os.path.realpath(__file__)), "test-media/../test-media/testReplay.SC2Replay"
        )
        with open(filename, "rb") as replayFile:
            return self.test_ac_api_client.publish_result(
                {
                    "match": match_id,
                    "type": result_type,
                    "replay_file": SimpleUploadedFile("replayFile.SC2Replay", replayFile.read()),
                    "game_steps": 500,
                },
            )

    def _post_to_results_no_bot1_data(self, match_id, result_type, bot_data_set, expected_code=201):
        filename = os.path.join(
            os.path.dirname(os.path.realpath(__file__)), "test-media/../test-media/testReplay.SC2Replay"
        )
        with (
            open(filename, "rb") as replay_file,
            open(TestAssetPaths.test_bot_datas["bot2"][bot_data_set]["path"], "rb") as bot2_data,
        ):
            return self.test_ac_api_client.submit_custom_result(
                match_id,
                result_type,
                replay_file,
                "",
                bot2_data,
                "",
                "",
                "",
                expected_code=expected_code,
            )

    def _post_to_results_no_bot2_data(self, match_id, result_type, bot_data_set, expected_code=201):
        filename = os.path.join(
            os.path.dirname(os.path.realpath(__file__)), "test-media/../test-media/testReplay.SC2Replay"
        )
        with (
            open(filename, "rb") as replay_file,
            open(TestAssetPaths.test_bot_datas["bot1"][bot_data_set]["path"], "rb") as bot1_data,
        ):
            return self.test_ac_api_client.submit_custom_result(
                match_id,
                result_type,
                replay_file,
                bot1_data,
                "",
                "",
                "",
                "",
                expected_code=expected_code,
            )

    def _post_to_results_no_replay(self, match_id, result_type, expected_code=201):
        return self.test_ac_api_client.publish_result(
            {"match": match_id, "type": result_type, "replay_file": "", "game_steps": 500},
            expected_code=expected_code,
        )

    def _post_to_results_no_replay_updated_datas(self, match_id, result_type):
        filename = os.path.join(
            os.path.dirname(os.path.realpath(__file__)), "test-media/../test-media/testReplay.SC2Replay"
        )
        with (
            open(filename, "rb"),
            open(TestAssetPaths.test_bot_datas["bot1"][0]["path"], "rb") as bot2_data,
            open(TestAssetPaths.test_bot_datas["bot2"][0]["path"], "rb") as bot1_data,
            open(TestAssetPaths.test_bot1_match_log_path, "rb") as bot1_log,
            open(TestAssetPaths.test_bot2_match_log_path, "rb") as bot2_log,
            open(TestAssetPaths.test_arenaclient_log_path, "rb"),
        ):
            return self.test_ac_api_client.publish_result(
                {
                    "match": match_id,
                    "type": result_type,
                    "replay_file": "",
                    "game_steps": 500,
                    "bot1_data": SimpleUploadedFile("bot1_data.zip", bot1_data.read()),
                    "bot2_data": SimpleUploadedFile("bot2_data.zip", bot2_data.read()),
                    "bot1_log": SimpleUploadedFile("bot1_log.zip", bot1_log.read()),
                    "bot2_log": SimpleUploadedFile("bot2_log.zip", bot2_log.read()),
                }
            )

    def _generate_full_data_set(self):
        self.test_client.login(User.objects.get(username="staff_user"))

        self._generate_extra_users()
        self._generate_extra_bots()

        self._generate_match_activity()

        # generate a bot match request to ensure it doesn't bug things out
        from aiarena.core.services import bots

        game_mode = GameMode.objects.get(name="Melee")
        bots_list = bots.get_available(Bot.objects.all())
        match_requests.request_match(
            self.regularUser2, bots_list[0], bots.get_random_active_bot_excluding(bots_list[0].id), game_mode=game_mode
        )

        # generate match requests from regularUser1
        bot = bots.get_random_active()
        match_requests.request_match(
            self.regularUser1, bot, bots.get_random_active_bot_excluding(bot.id), game_mode=game_mode
        )
        match_requests.request_match(
            self.regularUser1, bot, bots.get_random_active_bot_excluding(bot.id), game_mode=game_mode
        )
        bot = bots.get_random_active()
        match_requests.request_match(
            self.regularUser1, bot, bots.get_random_active_bot_excluding(bot.id), game_mode=game_mode
        )

        self.test_client.logout()  # child tests can login if they require

    def _generate_match_activity(self):
        match_id = self._post_to_matches().data["id"]
        self._post_to_results_no_replay(match_id, "InitializationError")

        match_id = self._post_to_matches().data["id"]
        self._post_to_results(match_id, "MatchCancelled")

        match_id = self._post_to_matches().data["id"]
        self._post_to_results_no_bot1_data(match_id, "Player1Win", 0)

        match_id = self._post_to_matches().data["id"]
        self._post_to_results_no_bot2_data(match_id, "Player1Crash", 0)

        match_id = self._post_to_matches().data["id"]
        self._post_to_results(match_id, "Player1TimeOut")

        match_id = self._post_to_matches().data["id"]
        self._post_to_results_no_bot_datas(match_id, "Player2Win")

        match_id = self._post_to_matches().data["id"]
        self._post_to_results_no_bot_datas(match_id, "Player2Crash")

        match_id = self._post_to_matches().data["id"]
        self._post_to_results(match_id, "Player2TimeOut")

        match_id = self._post_to_matches().data["id"]
        self._post_to_results(match_id, "Tie")

        match_id = self._post_to_matches().data["id"]
        self._post_to_results_no_replay(match_id, "Error")

    def _generate_extra_bots(self):
        competition = Competition.objects.order_by("id").first()
        zerg = BotRace.objects.get(label="Z")
        self.regularUser2Bot1 = self._create_bot(self.regularUser2, "regularUser2Bot1")
        self.regularUser2Bot2 = self._create_active_bot_for_competition(
            competition.id, self.regularUser2, "regularUser2Bot2"
        )
        self.regularUser3Bot1 = self._create_active_bot_for_competition(
            competition.id, self.regularUser3, "regularUser3Bot1"
        )
        self.regularUser3Bot2 = self._create_active_bot_for_competition(
            competition.id, self.regularUser3, "regularUser3Bot2", zerg
        )
        self.regularUser4Bot1 = self._create_bot(self.regularUser4, "regularUser4Bot1")
        self.regularUser4Bot2 = self._create_bot(self.regularUser4, "regularUser4Bot2")

    def _generate_extra_users(self):
        self.regularUser2 = WebsiteUser.objects.create_user(
            username="regular_user2", password="x", email="regular_user2@dev.aiarena.net"
        )
        self.regularUser3 = WebsiteUser.objects.create_user(
            username="regular_user3", password="x", email="regular_user3@dev.aiarena.net"
        )
        self.regularUser4 = WebsiteUser.objects.create_user(
            username="regular_user4", password="x", email="regular_user4@dev.aiarena.net"
        )


class LoggedInMixin(BaseTestMixin):
    """
    A test case for when logged in as a user.
    """

    def setUp(self):
        super().setUp()
        self.staffUser1 = WebsiteUser.objects.create_user(
            username="staff_user",
            password="x",
            email="staff_user@dev.aiarena.net",
            is_staff=True,
            is_superuser=True,
            is_active=True,
        )

        self.arenaclientUser1 = ArenaClient.objects.create(
            username="arenaclient1",
            email="arenaclient@dev.aiarena.net",
            type="ARENA_CLIENT",
            trusted=True,
            owner=self.staffUser1,
        )
        self.test_ac_api_client.set_api_token(Token.objects.create(user=self.arenaclientUser1).key)
        self.regularUser1 = WebsiteUser.objects.create_user(
            username="regular_user1", password="x", email="regular_user1@dev.aiarena.net"
        )


class MatchReadyMixin(LoggedInMixin):
    """
    A test case which is setup and ready to run matches
    """

    def setUp(self):
        super().setUp()

        # raise the configured per user limits
        settings.MAX_USER_BOT_PARTICIPATIONS_ACTIVE_FREE_TIER = 10
        config.MAX_USER_BOT_COUNT = 10

        self.test_client.login(self.staffUser1)
        competition = self._create_game_mode_and_open_competition()
        m1 = self._create_map_for_competition("testmap1", competition.id)

        terran = BotRace.terran()
        zerg = BotRace.zerg()
        protoss = BotRace.protoss()

        self.regularUser1Bot1 = self._create_active_bot_for_competition(
            competition.id, self.regularUser1, "regularUser1Bot1", terran
        )
        self.regularUser1Bot2 = self._create_active_bot_for_competition(
            competition.id, self.regularUser1, "regularUser1Bot2", zerg
        )
        self.regularUser1Bot3_Inactive = self._create_bot(
            self.regularUser1, "regularUser1Bot3", protoss
        )  # inactive bot for realism
        self.staffUser1Bot1 = self._create_active_bot_for_competition(
            competition.id, self.staffUser1, "staffUser1Bot1", terran
        )
        self.staffUser1Bot2 = self._create_active_bot_for_competition(
            competition.id, self.staffUser1, "staffUser1Bot2", zerg
        )

        # add another competition
        game_mode = GameMode.objects.first()
        competition2 = self._create_open_competition(game_mode.id, "Competition 2")
        m2 = self._create_map_for_competition("testmap2", competition2.id)

        self._create_map_for_game_mode("testmap3", competition.game_mode_id)

        map_pool = MapPool.objects.create(name="Map pool 1")
        map_pool.maps.add(m1)
        map_pool.maps.add(m2)

        # use some existing bots
        CompetitionParticipation.objects.create(bot_id=self.regularUser1Bot1.id, competition_id=competition2.id)
        CompetitionParticipation.objects.create(bot_id=self.staffUser1Bot1.id, competition_id=competition2.id)
        # and also create some new bots
        self.regularUser1Bot4 = self._create_active_bot_for_competition(
            competition2.id, self.regularUser1, "regularUser1Bot4", protoss
        )
        self.staffUser1Bot3 = self._create_active_bot_for_competition(
            competition2.id, self.staffUser1, "staffUser1Bot3", protoss
        )


class FullDataSetMixin(MatchReadyMixin):
    """
    A test case with a full dataset including run matches.
    """

    def setUp(self):
        super().setUp()
        self._generate_full_data_set()
