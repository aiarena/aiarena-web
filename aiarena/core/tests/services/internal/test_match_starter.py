from django.test import TestCase
from django.utils import timezone

from aiarena.core.models import ArenaClient, Bot, Competition, Game, GameMode, Map, Match, MatchParticipation, User
from aiarena.core.models.bot_race import BotRace
from aiarena.core.services.service_implementations.internal.match_starter import MatchStarter
from aiarena.core.tests.testing_utils import create_bot_for_competition


class LadderMatchStarterTests(TestCase):
    def setUp(self):
        self.user = User.objects.create(username="testuser", email="testemail")
        self.arenaclient = ArenaClient.objects.create(trusted=True, owner=self.user)
        self.bot1, self.bot2, self.map = self.create_participant_bots_and_map()

    def create_participant_bots_and_map(self) -> (Bot, Bot, Map):
        # todo: this should be in a fixture or factory
        game = Game.objects.create(name="testgame")
        game_mode = GameMode.objects.create(name="testgamemode", game=game)
        BotRace.create_all_races()
        bot_race = BotRace.objects.first()
        competition = Competition.objects.create(name="testcompetition", game_mode=game_mode)
        competition.playable_races.add(bot_race)
        competition.open()
        match_map = Map.objects.create(name="testmap", game_mode=game_mode)

        # create two participants
        bot1 = create_bot_for_competition(
            competition=competition, for_user=self.user, bot_name="testbot1", bot_type="python", bot_race=bot_race
        )
        bot2 = create_bot_for_competition(
            competition=competition, for_user=self.user, bot_name="testbot2", bot_type="python", bot_race=bot_race
        )
        return bot1, bot2, match_map

    def create_test_match(self, bot1, bot2, match_map, is_requested_match=False):
        requested_by_user = self.user if is_requested_match else None
        match = Match.objects.create(map=match_map, require_trusted_arenaclient=True, requested_by=requested_by_user)
        MatchParticipation.objects.create(match=match, participant_number=1, bot=bot1)
        MatchParticipation.objects.create(match=match, participant_number=2, bot=bot2)
        return match

    def test_match_starts_successfully_with_trusted_client_and_available_participants(self):
        match = self.create_test_match(self.bot1, self.bot2, self.map)
        result = MatchStarter.start(match, self.arenaclient)
        self.assertTrue(result)

    def test_match_fails_to_start_if_arenaclient_is_not_trusted(self):
        self.arenaclient.trusted = False
        match = self.create_test_match(self.bot1, self.bot2, self.map)
        result = MatchStarter.start(match, self.arenaclient)
        self.assertFalse(result)

    def test_match_fails_to_start_if_already_started(self):
        match = self.create_test_match(self.bot1, self.bot2, self.map)
        match.started = timezone.now()
        match.save()
        result = MatchStarter.start(match, self.arenaclient)
        self.assertFalse(result)

    def test_match_starts_successfully_in_parallel_when_both_bot_datas_not_in_use(self):
        """
        Tests that a match can start in parallel with another match when both match participants
         have bot data disabled.
        """
        self.start_matches_and_assert_result(
            test_match_definitions=[
                {
                    # Match 1
                    "expect_success": True,
                    "use_bot_data_for_participant1": False,
                    "use_bot_data_for_participant2": False,
                    "update_bot_data_for_participant1": False,
                    "update_bot_data_for_participant2": False,
                },
                {
                    # Match 2
                    "expect_success": True,
                    "use_bot_data_for_participant1": False,
                    "use_bot_data_for_participant2": False,
                    "update_bot_data_for_participant1": False,
                    "update_bot_data_for_participant2": False,
                },
            ]
        )

    def test_match_starts_successfully_in_parallel_when_one_bot_data_is_in_use(self):
        """
        Tests that a match can start in parallel with another match when only one match participant
         has bot data enabled.
        """
        self.start_matches_and_assert_result(
            test_match_definitions=[
                {
                    # Match 1
                    "expect_success": True,
                    "use_bot_data_for_participant1": True,
                    "use_bot_data_for_participant2": False,
                    "update_bot_data_for_participant1": False,
                    "update_bot_data_for_participant2": False,
                },
                {
                    # Match 2
                    "expect_success": True,
                    "use_bot_data_for_participant1": True,
                    "use_bot_data_for_participant2": False,
                    "update_bot_data_for_participant1": False,
                    "update_bot_data_for_participant2": False,
                },
            ]
        )

    def test_match_starts_successfully_in_parallel_when_bot_data_was_previously_in_use_but_now_isnt(self):
        """
        Tests that a match can start in parallel with another match when a match participant
         had bot data enabled but is now disabled.
        """
        self.start_matches_and_assert_result(
            test_match_definitions=[
                {
                    # Match 1
                    "expect_success": True,
                    "use_bot_data_for_participant1": True,
                    "use_bot_data_for_participant2": False,
                    "update_bot_data_for_participant1": False,
                    "update_bot_data_for_participant2": False,
                },
                {
                    # Match 2
                    "expect_success": True,
                    "use_bot_data_for_participant1": False,
                    "use_bot_data_for_participant2": False,
                    "update_bot_data_for_participant1": False,
                    "update_bot_data_for_participant2": False,
                },
            ]
        )

    def test_match_starts_successfully_in_parallel_when_bot_data_wasnt_in_use_but_now_is(self):
        """
        Tests that a match can start in parallel with another match when a match participant
         had bot data disabled but is now enabled.
        """
        self.start_matches_and_assert_result(
            test_match_definitions=[
                {
                    # Match 1
                    "expect_success": True,
                    "use_bot_data_for_participant1": False,
                    "use_bot_data_for_participant2": False,
                    "update_bot_data_for_participant1": False,
                    "update_bot_data_for_participant2": False,
                },
                {
                    # Match 2
                    "expect_success": True,
                    "use_bot_data_for_participant1": True,
                    "use_bot_data_for_participant2": False,
                    "update_bot_data_for_participant1": False,
                    "update_bot_data_for_participant2": False,
                },
            ]
        )

    def test_match_starts_successfully_in_parallel_when_bot_data_is_in_use(self):
        """
        Tests that a match can start in parallel with another match when both match participants
            have bot data enabled.
        """
        self.start_matches_and_assert_result(
            test_match_definitions=[
                {
                    # Match 1
                    "expect_success": True,
                    "use_bot_data_for_participant1": True,
                    "use_bot_data_for_participant2": True,
                    "update_bot_data_for_participant1": False,
                    "update_bot_data_for_participant2": False,
                },
                {
                    # Match 2
                    "expect_success": True,
                    "use_bot_data_for_participant1": True,
                    "use_bot_data_for_participant2": True,
                    "update_bot_data_for_participant1": False,
                    "update_bot_data_for_participant2": False,
                },
            ]
        )

    def test_competition_match_fails_to_start_in_parallel_when_bot_data_was_updateable_but_now_isnt(self):
        """
        Tests that a match from a competition fails to start in parallel with another match when a match participant
            had bot data enabled for updates but updates are now disabled.
            If this didn't fail, then the new match could be played with old data, which wouldn't be a huge issue, but
            blocking that situation seems more elegant.
        """
        self.start_matches_and_assert_result(
            test_match_definitions=[
                {
                    # Match 1
                    "expect_success": True,
                    "use_bot_data_for_participant1": True,
                    "use_bot_data_for_participant2": True,
                    "update_bot_data_for_participant1": True,
                    "update_bot_data_for_participant2": False,
                },
                {
                    # Match 2
                    "expect_success": False,
                    "use_bot_data_for_participant1": True,
                    "use_bot_data_for_participant2": True,
                    "update_bot_data_for_participant1": False,
                    "update_bot_data_for_participant2": False,
                },
            ]
        )

    def test_requested_match_successfully_starts_in_parallel_when_bot_data_was_updateable_but_now_isnt(self):
        """
        Tests that a requested match successfully starts in parallel with another match when a match participant
            had bot data enabled for updates but updates are now disabled.

            This is specifically to ensure that requested matches are not blocked by other matches from starting when
            said other matches are updating bot data, because it is assumed that bot authors don't care as much
            about the data being up-to-date for requested matches.
        """
        self.start_matches_and_assert_result(
            test_match_definitions=[
                {
                    # Match 1
                    "expect_success": True,
                    "use_bot_data_for_participant1": True,
                    "use_bot_data_for_participant2": True,
                    "update_bot_data_for_participant1": True,
                    "update_bot_data_for_participant2": False,
                },
                {
                    # Match 2
                    "expect_success": True,
                    "use_bot_data_for_participant1": True,
                    "use_bot_data_for_participant2": True,
                    "update_bot_data_for_participant1": False,
                    "update_bot_data_for_participant2": False,
                    "is_requested_match": True,
                },
            ]
        )

    def test_match_starts_successfully_in_parallel_when_bot_data_wasnt_updateable_but_now_is(self):
        """
        Tests that a match starts successfully in parallel with another match when a match participant
            had bot data disabled for updates but updates are now enabled.
        """
        self.start_matches_and_assert_result(
            test_match_definitions=[
                {
                    # Match 1
                    "expect_success": True,
                    "use_bot_data_for_participant1": True,
                    "use_bot_data_for_participant2": True,
                    "update_bot_data_for_participant1": False,
                    "update_bot_data_for_participant2": False,
                },
                {
                    # Match 2
                    "expect_success": True,
                    "use_bot_data_for_participant1": True,
                    "use_bot_data_for_participant2": True,
                    "update_bot_data_for_participant1": True,
                    "update_bot_data_for_participant2": False,
                },
            ]
        )

    def test_match_fails_to_start_in_parallel_when_bot_data_is_updateable(self):
        """
        Tests that a match starts successfully in parallel with another match when a match participant
            has bot data updates enabled
        """
        self.start_matches_and_assert_result(
            test_match_definitions=[
                {
                    # Match 1
                    "expect_success": True,
                    "use_bot_data_for_participant1": True,
                    "use_bot_data_for_participant2": True,
                    "update_bot_data_for_participant1": True,
                    "update_bot_data_for_participant2": False,
                },
                {
                    # Match 2
                    "expect_success": False,
                    "use_bot_data_for_participant1": True,
                    "use_bot_data_for_participant2": True,
                    "update_bot_data_for_participant1": True,
                    "update_bot_data_for_participant2": False,
                },
            ]
        )

    def test_match_fails_to_start_in_parallel_when_both_bot_datas_are_updateable(self):
        """
        Tests that a match starts successfully in parallel with another match when both match participants
            have bot data updates enabled
        """
        self.start_matches_and_assert_result(
            test_match_definitions=[
                {
                    # Match 1
                    "expect_success": True,
                    "use_bot_data_for_participant1": True,
                    "use_bot_data_for_participant2": True,
                    "update_bot_data_for_participant1": True,
                    "update_bot_data_for_participant2": True,
                },
                {
                    # Match 2
                    "expect_success": False,
                    "use_bot_data_for_participant1": True,
                    "use_bot_data_for_participant2": True,
                    "update_bot_data_for_participant1": True,
                    "update_bot_data_for_participant2": True,
                },
            ]
        )

    def test_match_starts_successfully_in_parallel_when_bot_data_was_previously_updateable_but_now_not_in_use(self):
        """
        Tests that a match can start in parallel with another match when a previous match participant
            had bot data enabled for updates but the new match has bot data entirely disabled.
        """
        self.start_matches_and_assert_result(
            test_match_definitions=[
                {
                    # Match 1
                    "expect_success": True,
                    "use_bot_data_for_participant1": True,
                    "use_bot_data_for_participant2": False,
                    "update_bot_data_for_participant1": True,
                    "update_bot_data_for_participant2": False,
                },
                {
                    # Match 2
                    "expect_success": True,
                    "use_bot_data_for_participant1": False,
                    "use_bot_data_for_participant2": False,
                    "update_bot_data_for_participant1": False,
                    "update_bot_data_for_participant2": False,
                },
            ]
        )

    def start_matches_and_assert_result(self, test_match_definitions):
        for test_definition in test_match_definitions:
            self.start_new_match_and_assert_result(
                expect_success=test_definition["expect_success"],
                use_bot_data_for_participant1=test_definition["use_bot_data_for_participant1"],
                use_bot_data_for_participant2=test_definition["use_bot_data_for_participant2"],
                update_bot_data_for_participant1=test_definition["update_bot_data_for_participant1"],
                update_bot_data_for_participant2=test_definition["update_bot_data_for_participant2"],
                is_requested_match=test_definition.get("is_requested_match", False),
            )

    def start_new_match_and_assert_result(
        self,
        expect_success: bool,
        use_bot_data_for_participant1,
        use_bot_data_for_participant2,
        update_bot_data_for_participant1,
        update_bot_data_for_participant2,
        is_requested_match=False,
    ):
        match = self.create_test_match(self.bot1, self.bot2, self.map, is_requested_match)
        self.set_use_bot_data(match, use_bot_data_for_participant1, use_bot_data_for_participant2)
        self.set_update_bot_data(match, update_bot_data_for_participant1, update_bot_data_for_participant2)
        result = MatchStarter.start(match, self.arenaclient)
        self.assertEqual(expect_success, result)

    def set_use_bot_data(self, match: Match, use_bot_data_for_participant1: bool, use_bot_data_for_participant2: bool):
        p1 = match.participant1
        p1.use_bot_data = use_bot_data_for_participant1
        p1.save()
        p2 = match.participant2
        p2.use_bot_data = use_bot_data_for_participant2
        p2.save()

    def set_update_bot_data(
        self, match: Match, update_bot_data_for_participant1: bool, update_bot_data_for_participant2: bool
    ):
        p1 = match.participant1
        p1.update_bot_data = update_bot_data_for_participant1
        p1.save()
        p2 = match.participant2
        p2.update_bot_data = update_bot_data_for_participant2
        p2.save()
