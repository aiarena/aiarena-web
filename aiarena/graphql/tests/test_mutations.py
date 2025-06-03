from django.conf import settings

import pytest

from aiarena.core.models import Bot, CompetitionParticipation, Match, MatchParticipation
from aiarena.core.tests.base import GraphQLTest
from aiarena.graphql import BotType, CompetitionType, MapPoolType, MapType


class TestRequestMatch(GraphQLTest):
    mutation_name = "requestMatch"
    mutation = """
        mutation ($input: RequestMatchInput!) {
            requestMatch(input: $input) {
                errors {
                    messages
                    field
                }
            }
        }
    """

    def test_specific_matchup_specific_map_success(self, user, bot, other_bot, map):
        """
        Test creating a match request with a specific opponent, and a specific map.
        """
        assert not Match.objects.filter(requested_by=user).exists()

        self.mutate(
            login_user=user,
            expected_status=200,
            variables={
                "input": {
                    "agent1": self.to_global_id(BotType, bot.id),
                    "agent2": self.to_global_id(BotType, other_bot.id),
                    "mapSelectionType": "specific_map",
                    "chosenMap": self.to_global_id(MapType, map.id),
                    "matchCount": 1,
                }
            },
        )

        match = Match.objects.get(requested_by=user)
        assert match.status == "Queued"
        assert match.map

        match_participation_bot_1 = MatchParticipation.objects.get(bot=bot)
        match_participation_bot_2 = MatchParticipation.objects.get(bot=other_bot)

        assert match_participation_bot_1.bot == bot
        assert match_participation_bot_2.bot == other_bot
        assert match_participation_bot_1.match == match
        assert match_participation_bot_2.match == match

    def test_specific_matchup_map_pool_success(self, user, bot, other_bot, map_pool):
        """
        Test creating a match request with a specific opponent, and a map pool.
        """
        assert not Match.objects.filter(requested_by=user).exists()

        self.mutate(
            login_user=user,
            expected_status=200,
            variables={
                "input": {
                    "agent1": self.to_global_id(BotType, bot.id),
                    "agent2": self.to_global_id(BotType, other_bot.id),
                    "mapSelectionType": "map_pool",
                    "matchCount": 1,
                    "mapPool": self.to_global_id(MapPoolType, map_pool.id),
                }
            },
        )
        match = Match.objects.get(requested_by=user)
        assert match.status == "Queued"
        assert match.map

        match_participation_bot_1 = MatchParticipation.objects.get(bot=bot)
        match_participation_bot_2 = MatchParticipation.objects.get(bot=other_bot)
        assert match_participation_bot_1.bot == bot
        assert match_participation_bot_2.bot == other_bot
        assert match_participation_bot_1.match == match
        assert match_participation_bot_2.match == match

    def test_not_logged_in(self, user, bot, other_bot, map_pool):
        assert not Match.objects.filter(requested_by=user).exists()

        self.mutate(
            variables={
                "input": {
                    "agent1": self.to_global_id(BotType, bot.id),
                    "agent2": self.to_global_id(BotType, other_bot.id),
                    "mapSelectionType": "map_pool",
                    "matchCount": 1,
                    "mapPool": self.to_global_id(MapPoolType, map_pool.id),
                }
            },
            expected_errors_like=["You need to be logged in in to perform this action."],
        )
        assert not Match.objects.filter(requested_by=user).exists()

    def test_invalid_bot2(self, user, bot, map_pool):
        assert not Match.objects.filter(requested_by=user).exists()

        self.mutate(
            login_user=user,
            variables={
                "input": {
                    "agent1": self.to_global_id(BotType, bot.id),
                    "mapSelectionType": "map_pool",
                    "matchCount": 1,
                    "agent2": 999,
                    "mapPool": self.to_global_id(MapPoolType, map_pool.id),
                }
            },
            expected_errors_like=['Error processing agent2: Unable to parse global ID "999".'],
        )
        assert not Match.objects.filter(requested_by=user).exists()

    def test_no_bot2(self, user, bot, map_pool):
        assert not Match.objects.filter(requested_by=user).exists()

        self.mutate(
            login_user=user,
            variables={
                "input": {
                    "agent1": self.to_global_id(BotType, bot.id),
                    "mapSelectionType": "map_pool",
                    "matchCount": 1,
                    "mapPool": self.to_global_id(MapPoolType, map_pool.id),
                }
            },
            expected_validation_errors={"agent2": ["Required field"]},
        )
        assert not Match.objects.filter(requested_by=user).exists()

    def test_invalid_bot1(self, user, bot, other_bot, map_pool):
        assert not Match.objects.filter(requested_by=user).exists()

        self.mutate(
            login_user=user,
            variables={
                "input": {
                    "agent1": 999,
                    "agent2": self.to_global_id(BotType, other_bot.id),
                    "mapSelectionType": "map_pool",
                    "matchCount": 1,
                    "mapPool": self.to_global_id(MapPoolType, map_pool.id),
                }
            },
            expected_errors_like=['Error processing agent1: Unable to parse global ID "999".'],
        )
        assert not Match.objects.filter(requested_by=user).exists()

    def test_no_bot1(self, user, bot, other_bot, map_pool):
        assert not Match.objects.filter(requested_by=user).exists()

        self.mutate(
            login_user=user,
            variables={
                "input": {
                    "mapSelectionType": "map_pool",
                    "matchCount": 1,
                    "agent2": self.to_global_id(BotType, other_bot.id),
                    "mapPool": self.to_global_id(MapPoolType, map_pool.id),
                }
            },
            expected_validation_errors={"agent1": ["Required field"]},
        )
        assert not Match.objects.filter(requested_by=user).exists()

    def test_invalid_map_selection_type(self, user, bot, other_bot, map_pool):
        assert not Match.objects.filter(requested_by=user).exists()

        self.mutate(
            login_user=user,
            variables={
                "input": {
                    "agent1": self.to_global_id(BotType, bot.id),
                    "agent2": self.to_global_id(BotType, other_bot.id),
                    "mapSelectionType": "dodecahedron",
                    "matchCount": 1,
                    "mapPool": self.to_global_id(MapPoolType, map_pool.id),
                }
            },
            expected_errors_like=["'mapSelectionType' must be set to 'specific_map' or 'map_pool'."],
        )
        assert not Match.objects.filter(requested_by=user).exists()

    def test_no_map_selection_type(self, user, bot, other_bot, map_pool):
        assert not Match.objects.filter(requested_by=user).exists()

        self.mutate(
            login_user=user,
            variables={
                "input": {
                    "agent1": self.to_global_id(BotType, bot.id),
                    "agent2": self.to_global_id(BotType, other_bot.id),
                    "matchCount": 1,
                    "mapPool": self.to_global_id(MapPoolType, map_pool.id),
                }
            },
            expected_errors_like=["'mapSelectionType' must be set to 'specific_map' or 'map_pool'."],
        )
        assert not Match.objects.filter(requested_by=user).exists()

    def test_high_match_count(self, user, bot, other_bot, map_pool):
        assert not Match.objects.filter(requested_by=user).exists()

        self.mutate(
            login_user=user,
            variables={
                "input": {
                    "agent1": self.to_global_id(BotType, bot.id),
                    "agent2": self.to_global_id(BotType, other_bot.id),
                    "mapSelectionType": "map_pool",
                    "matchCount": 500,
                    "mapPool": self.to_global_id(MapPoolType, map_pool.id),
                }
            },
            expected_errors_like=["Error requesting match: That number of matches exceeds your match request limit."],
        )
        assert not Match.objects.filter(requested_by=user).exists()

    def test_no_match_count(self, user, bot, other_bot, map_pool):
        assert not Match.objects.filter(requested_by=user).exists()

        self.mutate(
            login_user=user,
            variables={
                "input": {
                    "agent1": self.to_global_id(BotType, bot.id),
                    "agent2": self.to_global_id(BotType, other_bot.id),
                    "mapSelectionType": "map_pool",
                    "mapPool": self.to_global_id(MapPoolType, map_pool.id),
                }
            },
            expected_validation_errors={"matchCount": ["Required field"]},
        )
        assert not Match.objects.filter(requested_by=user).exists()

    def test_invalid_map_pool(self, user, bot, other_bot):
        assert not Match.objects.filter(requested_by=user).exists()

        self.mutate(
            login_user=user,
            variables={
                "input": {
                    "agent1": self.to_global_id(BotType, bot.id),
                    "agent2": self.to_global_id(BotType, other_bot.id),
                    "mapSelectionType": "map_pool",
                    "matchCount": 1,
                    "mapPool": 999,
                }
            },
            expected_errors_like=['Error processing mapPool: Unable to parse global ID "999".'],
        )
        assert not Match.objects.filter(requested_by=user).exists()

    def test_no_map_pool(self, user, bot, other_bot):
        assert not Match.objects.filter(requested_by=user).exists()

        self.mutate(
            login_user=user,
            variables={
                "input": {
                    "agent1": self.to_global_id(BotType, bot.id),
                    "agent2": self.to_global_id(BotType, other_bot.id),
                    "mapSelectionType": "map_pool",
                    "matchCount": 1,
                }
            },
            expected_errors_like=["Either 'mapPool' or 'chosenMap' must be provided."],
        )
        assert not Match.objects.filter(requested_by=user).exists()


class TestUpdateCompetitionParticipation(GraphQLTest):
    mutation_name = "updateCompetitionParticipation"
    mutation = """
        mutation ($input: UpdateCompetitionParticipationInput!) {
            updateCompetitionParticipation(input: $input) {
                errors {
                    messages
                    field
                }
            }
        }
    """

    def test_happy_path(self, bot, competition):
        """
        Test creating a competition participation.
        """
        # Make sure there are no existing competition participations
        assert not CompetitionParticipation.objects.filter(bot=bot, competition=competition).exists()

        # Create a competition participation
        self.mutate(
            login_user=bot.user,
            expected_status=200,
            variables={
                "input": {
                    "bot": self.to_global_id(BotType, bot.id),
                    "competition": self.to_global_id(CompetitionType, competition.id),
                    "active": True,
                }
            },
        )

        # Verify competition participation was created correctly
        competition_participation = CompetitionParticipation.objects.get(bot=bot, competition=competition)
        assert competition_participation.active
        assert competition_participation.division_num == CompetitionParticipation.DEFAULT_DIVISION

        # Verify that setting an active participation to active doesn't change active status
        self.mutate(
            login_user=bot.user,
            expected_status=200,
            variables={
                "input": {
                    "bot": self.to_global_id(BotType, bot.id),
                    "competition": self.to_global_id(CompetitionType, competition.id),
                    "active": True,
                }
            },
        )

        competition_participation = CompetitionParticipation.objects.get(bot=bot, competition=competition)
        assert competition_participation.active
        assert competition_participation.division_num == CompetitionParticipation.DEFAULT_DIVISION

        competition_participation.division_num = 1
        competition_participation.save()

        # Leave the competition i.e. set active to false, and make sure division is reset to 0
        self.mutate(
            login_user=bot.user,
            expected_status=200,
            variables={
                "input": {
                    "bot": self.to_global_id(BotType, bot.id),
                    "competition": self.to_global_id(CompetitionType, competition.id),
                    "active": False,
                }
            },
        )

        competition_participation.refresh_from_db()
        assert not competition_participation.active
        assert competition_participation.division_num == CompetitionParticipation.DEFAULT_DIVISION
        # Verify that setting an inactive participation to inactive doesn't change active status

        self.mutate(
            login_user=bot.user,
            expected_status=200,
            variables={
                "input": {
                    "bot": self.to_global_id(BotType, bot.id),
                    "competition": self.to_global_id(CompetitionType, competition.id),
                    "active": False,
                }
            },
        )
        assert not competition_participation.active
        assert competition_participation.division_num == CompetitionParticipation.DEFAULT_DIVISION

        # Reactivate the competition i.e. set active to true
        self.mutate(
            login_user=bot.user,
            expected_status=200,
            variables={
                "input": {
                    "bot": self.to_global_id(BotType, bot.id),
                    "competition": self.to_global_id(CompetitionType, competition.id),
                    "active": True,
                }
            },
        )

        competition_participation.refresh_from_db()
        assert competition_participation.active

    def test_join_closed_competiton(self, competition_factory, game_mode, bot):
        closed_competition = competition_factory(name="A closed Competition", status="closed", game_mode=game_mode)
        assert not CompetitionParticipation.objects.filter(bot=bot, competition=closed_competition).exists()
        # Create a competition participation
        self.mutate(
            login_user=bot.user,
            expected_status=200,
            variables={
                "input": {"competition": self.to_global_id(CompetitionType, closed_competition.id), "active": True}
            },
            expected_errors_like={"This competition is closed."},
        )
        assert not CompetitionParticipation.objects.filter(bot=bot, competition=closed_competition).exists()

    def test_required_field_not_specified(self, competition, bot):
        assert not CompetitionParticipation.objects.filter(bot=bot, competition=competition).exists()

        # Create a competition participation
        self.mutate(
            login_user=bot.user,
            expected_status=200,
            variables={"input": {"competition": self.to_global_id(CompetitionType, competition.id), "active": True}},
            expected_validation_errors={"bot": ["Required field"]},
        )

    def test_active_field_not_boolean(self, competition, bot):
        assert not CompetitionParticipation.objects.filter(bot=bot, competition=competition).exists()

        # Create a competition participation
        self.mutate(
            login_user=bot.user,
            expected_status=400,
            variables={
                "input": {
                    "bot": self.to_global_id(BotType, bot.id),
                    "competition": self.to_global_id(CompetitionType, competition.id),
                    "active": "Innocent robot'); DROP TABLE ROBOTS; --",
                }
            },
            expected_errors_like={"Boolean cannot represent a non boolean value"},
        )

    def test_invalid_bot_id(self, competition, bot):
        assert not CompetitionParticipation.objects.filter(bot=bot, competition=competition).exists()

        # Create a competition participation
        self.mutate(
            login_user=bot.user,
            expected_status=200,
            variables={
                "input": {
                    "bot": "Abracadabra",
                    "competition": self.to_global_id(CompetitionType, competition.id),
                    "active": True,
                }
            },
            expected_validation_errors={
                "bot": [
                    'Unable to parse global ID "Abracadabra". Make sure it is a base64 encoded string in the format: "TypeName:id". Exception message: Invalid Global ID'
                ]
            },
        )

    def test_invalid_competition_id(self, competition, bot):
        assert not CompetitionParticipation.objects.filter(bot=bot, competition=competition).exists()

        # Create a competition participation
        self.mutate(
            login_user=bot.user,
            expected_status=200,
            variables={
                "input": {
                    "bot": self.to_global_id(BotType, bot.id),
                    "competition": "Abracadabra",
                    "active": True,
                }
            },
            expected_validation_errors={
                "competition": [
                    'Unable to parse global ID "Abracadabra". Make sure it is a base64 encoded string in the format: "TypeName:id". Exception message: Invalid Global ID'
                ]
            },
        )

    def test_update_competition_participation_unauthorized(self, competition, bot, other_user):
        assert not CompetitionParticipation.objects.filter(bot=bot, competition=competition).exists()

        # Create a competition participation with other_user.
        self.mutate(
            login_user=other_user,
            expected_status=200,
            variables={
                "input": {
                    "bot": self.to_global_id(BotType, bot.id),
                    "competition": self.to_global_id(CompetitionType, competition.id),
                    "active": True,
                }
            },
            expected_errors_like=['bobby cannot perform "write" on "My_Bot"'],
        )
        # Verify the competition participation was not created.
        assert not CompetitionParticipation.objects.filter(bot=bot, competition=competition).exists()

    def test_update_competition_participation_insufficient_free_competitions(self, competition, bot, user, bot_factory):
        assert CompetitionParticipation.objects.filter(bot__user=user).count() == 0

        # Creating 4 bots
        bot_names = {0: "Zergelito", 1: "Probelito", 2: "Marinolito", 3: "Dronelito"}
        for i in range(4):
            bot_name = bot_names[i]
            extra_bot = bot_factory(user=user, name=bot_name)
            assert not CompetitionParticipation.objects.filter(bot=extra_bot, competition=competition).exists()
            self.mutate(
                login_user=user,
                expected_status=200,
                variables={
                    "input": {
                        "bot": self.to_global_id(BotType, extra_bot.id),
                        "competition": self.to_global_id(CompetitionType, competition.id),
                        "active": True,
                    }
                },
            )
            assert CompetitionParticipation.objects.filter(bot=extra_bot, competition=competition).exists()

        # Test that the 5th bot isn't created
        self.mutate(
            login_user=user,
            expected_status=200,
            variables={
                "input": {
                    "bot": self.to_global_id(BotType, bot.id),
                    "competition": self.to_global_id(CompetitionType, competition.id),
                    "active": True,
                }
            },
            expected_errors_like=["Too many active participations already exist for this user."],
        )
        # Verify the competition participation was not created.
        assert not CompetitionParticipation.objects.filter(bot=bot, competition=competition, active=True).exists()
        # assert CompetitionParticipation.objects.filter(bot__user=user).count() == 5


class TestUploadBot(GraphQLTest):
    mutation_name = "uploadBot"
    mutation = """
    mutation ($input: UploadBotInput!) {
        uploadBot(input: $input) {
            bot {
                id
            }
            errors {
                field
                messages
            }
        }
    }
    """

    @pytest.mark.parametrize(
        "bot_name,language,zip_fixture,expected_errors,should_create",
        [
            ("a_cpp_win_bot", "CPPWIN32", "cpp_win_zip_file", [], True),
            (
                "a_cpp_win_bot",
                "CPpWIN32",
                "invalid_python_zip_file",
                ["A bot of type cppwin32 would need to have a file in the zip file root named a_cpp_win_bot.exe"],
                False,
            ),
            ("a_cpp_lin_bot", "CPPLINUX", "cpp_lin_zip_file", [], True),
            (
                "a_cpp_lin_bot",
                "CPPLInUX",
                "invalid_python_zip_file",
                ["A bot of type cpplinux would need to have a file in the zip file root named a_cpp_lin_bot"],
                False,
            ),
            ("a_dot_net_bot", "DOTNETCORE", "dotnet_zip_file", [], True),
            (
                "a_dot_net_bot",
                "DOTnetCORE",
                "invalid_python_zip_file",
                ["A bot of type dotnetcore would need to have a file in the zip file root named a_dot_net_bot.dll"],
                False,
            ),
            ("a_java_bot", "JAVA", "java_zip_file", [], True),
            (
                "a_java_bot",
                "JaVA",
                "invalid_python_zip_file",
                ["A bot of type java would need to have a file in the zip file root named a_java_bot.jar"],
                False,
            ),
            ("a_node_js_bot", "NODEJS", "node_js_zip_file", [], True),
            (
                "a_node_js_bot",
                "NODEjS",
                "invalid_python_zip_file",
                ["A bot of type nodejs would need to have a file in the zip file root named a_node_js_bot.js"],
                False,
            ),
            ("a_python_bot", "PythoN", "python_zip_file", [], True),
            (
                "a_python_bot",
                "PythoN",
                "invalid_python_zip_file",
                ["A bot of type python would need to have a file in the zip file root named run.py"],
                False,
            ),
        ],
    )
    def test_upload_bot(
        self, user, get_fixture, all_bot_races, bot_name, language, zip_fixture, expected_errors, should_create
    ):
        assert not Bot.objects.filter(user=user).exists()
        self.mutate(
            login_user=user,
            expected_status=200,
            variables={
                "input": {
                    "name": bot_name,
                    "playsRace": "Z",
                    "botDataEnabled": False,
                    "type": language,
                    "botZip": None,
                }
            },
            files={"input.botZip": get_fixture(zip_fixture)},
            expected_errors_like=expected_errors,
        )
        assert Bot.objects.filter(user=user).exists() == should_create

        if should_create:
            bot = Bot.objects.get(user=user, name=bot_name)
            assert bot.user.id == user.id
            assert bot.bot_zip_publicly_downloadable is False
            assert bot.bot_data_enabled is False
            assert bot.bot_data_publicly_downloadable is False
            assert bot.get_wiki_article().current_revision.content == ""
            assert bot.get_bot_zip_limit_in_mb() == settings.CONSTANCE_CONFIG["BOT_ZIP_SIZE_LIMIT_IN_MB_FREE_TIER"][0]
        else:
            pass

    def test_upload_bot_bot_data_enabled(self, user, get_fixture, all_bot_races, python_zip_file):
        assert not Bot.objects.filter(user=user).exists()
        self.mutate(
            login_user=user,
            expected_status=200,
            variables={
                "input": {
                    "name": "NotMaru",
                    "playsRace": "T",
                    "botDataEnabled": True,
                    "type": "PYTHON",
                    "botZip": None,
                }
            },
            files={"input.botZip": python_zip_file()},
        )
        assert Bot.objects.filter(user=user).exists()

        bot = Bot.objects.get(user=user, name="NotMaru")
        assert bot.user.id == user.id
        assert bot.bot_zip_publicly_downloadable is False
        assert bot.bot_data_enabled is True
        assert bot.bot_data_publicly_downloadable is False
        assert bot.get_wiki_article().current_revision.content == ""
        assert bot.get_bot_zip_limit_in_mb() == settings.CONSTANCE_CONFIG["BOT_ZIP_SIZE_LIMIT_IN_MB_FREE_TIER"][0]

    def test_upload_bot_not_logged_in(self, all_bot_races, python_zip_file):
        assert Bot.objects.count() == 0
        self.mutate(
            login_user="",
            expected_status=200,
            variables={
                "input": {
                    "name": "NotSerral",
                    "playsRace": "Z",
                    "botDataEnabled": False,
                    "type": "PYTHON",
                    "botZip": None,
                }
            },
            files={"input.botZip": python_zip_file()},
            expected_errors_like=["You need to be logged in in to perform this action."],
        )
        assert Bot.objects.count() == 0

    def test_upload_bot_max_bots(self, user, all_bot_races, python_zip_file):
        # makes the max amount of bot count a default user can create

        assert not Bot.objects.filter(user=user).exists()

        max_bot_count = settings.CONSTANCE_CONFIG["MAX_USER_BOT_COUNT"][0]

        def get_bot_name(i):
            # creates a string like, a, b, c -> aa, ab, ac -> aaa, aab, aac
            name = ""
            while True:
                name = chr(97 + (i % 26)) + name
                i = i // 26 - 1
                if i < 0:
                    break
            return name

        # creates [max_bot_count]

        for i in range(max_bot_count):
            bot_name = get_bot_name(i)

            self.mutate(
                login_user=user,
                expected_status=200,
                variables={
                    "input": {
                        "name": bot_name,
                        "playsRace": "P",
                        "botDataEnabled": False,
                        "type": "PYTHON",
                        "botZip": None,
                    }
                },
                files={"input.botZip": python_zip_file()},
            )
            assert Bot.objects.filter(name=bot_name).exists()
        assert Bot.objects.filter(user=user).count() == max_bot_count

        self.mutate(
            login_user=user,
            expected_status=200,
            variables={
                "input": {
                    "name": "NotHarstem",
                    "playsRace": "P",
                    "botDataEnabled": False,
                    "type": "PYTHON",
                    "botZip": None,
                }
            },
            files={"input.botZip": python_zip_file()},
            expected_errors_like=[
                f"Maximum bot count of {max_bot_count} already reached. No more bots may be added for this user."
            ],
        )
        assert Bot.objects.filter(user=user).count() == max_bot_count


class TestUpdateBot(GraphQLTest):
    mutation_name = "updateBot"
    mutation = """
        mutation($input: UpdateBotInput!) {
            updateBot(input: $input) {
                bot {
                    id
                }
                errors {
                    field
                    messages
                }
            }
        }
    """

    def test_update_bot_success(self, user, bot, python_zip_file):
        """
        Test updating a bot with all fields set to True.
        """

        # We expect the bot fixture to be created with those values
        assert bot.user == user
        assert bot.bot_zip_publicly_downloadable is False
        assert bot.bot_data_enabled is False
        assert bot.bot_data_publicly_downloadable is False
        assert bot.get_wiki_article().current_revision.content == ""

        old_bot_zip_hash = bot.bot_zip
        old_bot_data_hash = bot.bot_data

        self.mutate(
            login_user=user,
            expected_status=200,
            variables={
                "input": {
                    "id": self.to_global_id(BotType, bot.id),
                    "botZipPubliclyDownloadable": True,
                    "botDataEnabled": True,
                    "botDataPubliclyDownloadable": True,
                    "wikiArticle": "#1Some Content",
                    "botZip": None,
                    "botData": None,
                }
            },
            files={
                "input.botZip": python_zip_file(),
                "input.botData": python_zip_file(),
            },
        )

        # Verify bot was updated correctly
        bot.refresh_from_db()
        assert bot.bot_zip_publicly_downloadable is True
        assert bot.bot_data_enabled is True
        assert bot.bot_data_publicly_downloadable is True
        assert bot.get_wiki_article().current_revision.content == "#1Some Content"
        assert bot.bot_zip != old_bot_zip_hash
        assert bot.bot_data != old_bot_data_hash

    def test_update_bot_invalid_bot_zip(self, user, bot, invalid_python_zip_file):
        """
        Test updating a bot with an invalid bot Zip.
        """

        self.mutate(
            login_user=user,
            expected_status=200,
            variables={
                "input": {
                    "id": self.to_global_id(BotType, bot.id),
                    "botZip": None,
                }
            },
            files={
                "input.botZip": invalid_python_zip_file(),
            },
            expected_errors_like=[
                "Incorrect bot zip file structure. A bot of type python would need to have a file in the zip file root named run.py"
            ],
        )

    def test_update_bot_unauthorized(self, user, other_user, bot):
        """
        Test updating a bot that does not belong to the user.
        """
        # We expect the bot fixture to be created with those values
        assert bot.user == user
        assert bot.bot_zip_publicly_downloadable is False
        assert bot.get_wiki_article().current_revision.content == ""

        self.mutate(
            login_user=other_user,
            variables={
                "input": {
                    "id": self.to_global_id(BotType, bot.id),
                    "botZipPubliclyDownloadable": True,
                    "wikiArticle": "Some Content",
                }
            },
            expected_errors_like=['bobby cannot perform "write" on "My_Bot"'],
        )

        # Verify bot was not updated
        bot.refresh_from_db()
        assert bot.bot_zip_publicly_downloadable is False
        assert bot.get_wiki_article().current_revision.content == ""

    def test_update_bot_unauthenticated(self, bot):
        """
        Test updating a bot without being authenticated.
        """
        # We expect the bot fixture to be created with those values
        assert bot.bot_zip_publicly_downloadable is False
        assert bot.get_wiki_article().current_revision.content == ""

        self.mutate(
            variables={
                "input": {
                    "id": self.to_global_id(BotType, bot.id),
                    "botZipPubliclyDownloadable": True,
                    "wikiArticle": "Some Content",
                }
            },
            expected_errors_like=['AnonymousUser cannot perform "write" on "My_Bot"'],
        )

        # Verify bot was not updated
        bot.refresh_from_db()
        assert bot.bot_zip_publicly_downloadable is False
        assert bot.get_wiki_article().current_revision.content == ""

    def test_required_field_not_specified(self, user, bot):
        """
        Test omitting a required field when updating the bot.
        """
        self.mutate(
            login_user=user,
            variables={"input": {"botZipPubliclyDownloadable": True, "wikiArticle": "Some Content"}},
            expected_validation_errors={"id": ["Required field"]},
        )

        # Verify bot was not updated
        bot.refresh_from_db()
        assert bot.bot_zip_publicly_downloadable is False
        assert bot.get_wiki_article().current_revision.content == ""

    def test_cannot_specify_attributes_not_in_input(self, user, bot):
        """
        Test that adding an extra field to the input results in an error.
        """
        self.mutate(
            login_user=user,
            variables={
                "input": {
                    "id": self.to_global_id(BotType, bot.id),
                    "name": "new name pls",
                }
            },
            expected_status=400,
            expected_errors_like=[
                "Field 'name' is not defined by type 'UpdateBotInput'.",
            ],
        )

        # Verify bot was not updated
        bot.refresh_from_db()
        assert bot.bot_zip_publicly_downloadable != "new name pls"
