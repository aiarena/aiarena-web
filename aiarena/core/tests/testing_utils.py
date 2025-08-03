from django.core.files import File
from django.test import Client
from django.urls import reverse

from rest_framework.authtoken.models import Token

from aiarena.core.models import ArenaClient, Bot, Competition, CompetitionParticipation, Map, MapPool, Match, User
from aiarena.core.models.bot_race import BotRace
from aiarena.core.models.game import Game
from aiarena.core.models.game_mode import GameMode


class TestAssetPaths:
    # For some reason using an absolute file path here will cause it to mangle the save directory and fail
    # later whilst handling the bot_zip file save
    test_bot_zip_path = "aiarena/core/tests/test-media/test_bot.zip"
    test_bot_zip_hash = "c96bcfc79318a8b50b0b2c8696400d06"
    test_bot_zip_updated_path = "aiarena/core/tests/test-media/test_bot_updated.zip"
    test_bot_zip_updated_hash = "685dba7a89511157a6594c20c50397d3"
    test_bot_datas = {
        "bot1": [
            {"path": "aiarena/core/tests/test-media/test_bot1_data0.zip", "hash": "8a2ed68ea1d98f699d7f03bd98c6530d"},
            {"path": "aiarena/core/tests/test-media/test_bot1_data1.zip", "hash": "c174816d0730c76cc649cf35b097d61e"},
        ],
        "bot2": [
            {"path": "aiarena/core/tests/test-media/test_bot2_data0.zip", "hash": "de998ff5944d17eb40e37429b162b651"},
            {"path": "aiarena/core/tests/test-media/test_bot2_data1.zip", "hash": "2d7ecb911b1da870a503acf4173be642"},
        ],
    }
    test_bot1_match_log_path = "aiarena/core/tests/test-media/test_bot1_match_log.zip"
    test_bot2_match_log_path = "aiarena/core/tests/test-media/test_bot2_match_log.zip"
    test_arenaclient_log_path = "aiarena/core/tests/test-media/test_arenaclient_log.zip"
    test_replay_path = "aiarena/core/tests/test-media/testReplay.SC2Replay"
    test_map_path = "aiarena/core/tests/test-media/AutomatonLE.SC2Map"


# These utility methods are placed here isntead of in the TestingClient, as the TestingClient operates through the
# Django admin interface. This is done to make clear that these methods operate in a different manner.
# It's possible that the TestingClient should be refactored to operate in the way these methods do, instead of using
# the admin interface


def create_game_races():
    BotRace.create_all_races()
    terran = BotRace.objects.get(label="T")
    zerg = BotRace.objects.get(label="Z")
    protoss = BotRace.objects.get(label="P")
    return protoss, terran, zerg


def create_bot_for_competition(
    competition: Competition, for_user: User, bot_name: str, bot_type: str, bot_race: BotRace
):
    with open(TestAssetPaths.test_bot_zip_path, "rb") as bot_zip:
        bot = Bot.objects.create(
            user=for_user, name=bot_name, plays_race=bot_race, type=bot_type, bot_zip=File(bot_zip)
        )
        CompetitionParticipation.objects.create(competition=competition, bot=bot)
        return bot


def create_arena_clients_with_matching_tokens(stdout, client, num_acs, for_user):
    ac_count = 0
    for x in range(num_acs):
        stdout.write(f"Creating ACs...{ac_count / num_acs * 100}%", ending="\r")
        ac = client.create_arenaclient(
            "aiarenaclient-" + str(x), "aiarenaclient-" + str(x) + "@dev.aiarena.net", for_user.id
        )
        Token.objects.create(user=ac, key=str(x))

    stdout.write("Creating ACs...100%")


def create_open_competition_with_map(client, name: str, game_mode_id: int, **competition_kwargs):
    competition = client.create_competition(name, game_mode_id, **competition_kwargs)
    with open(TestAssetPaths.test_map_path, "rb") as map:
        map = Map.objects.create(name="test_map1", file=File(map), game_mode_id=game_mode_id)
        map.competitions.add(competition)
    client.open_competition(competition.id)
    return competition


class TestingClient:
    TEST_PASSWORD = "x"

    def __init__(self, django_client=Client()):
        self.django_client = django_client

    def login(self, user: User):
        self.django_client.force_login(user)

    def logout(self):
        self.django_client.logout()

    def create_user(self, username: str, password: str, email: str, type: str, owner_id: int) -> User:
        if User.objects.filter(username=username).exists():
            raise Exception("That already exists!")

        url = reverse("admin:core_user_add")
        response = self.django_client.post(
            url,
            {
                "username": username,
                "password": password,
                "email": email,
                "type": type,
                "owner": owner_id,
            },
        )

        # we should be redirected back to the changelist
        assert response.status_code == 302 and response.url == reverse("admin:core_user_changelist")
        return User.objects.get(username=username)

    def create_arenaclient(self, username: str, email: str, owner_id: int, trusted=True) -> ArenaClient:
        if ArenaClient.objects.filter(username=username).exists():
            raise Exception("That already exists!")

        url = reverse("admin:core_arenaclient_add")
        response = self.django_client.post(
            url,
            {
                "username": username,
                "email": email,
                "password": self.TEST_PASSWORD,
                "type": "ARENA_CLIENT",
                "owner": owner_id,
                "trusted": trusted,
                "is_active": True,
            },
        )

        # we should be redirected back to the changelist
        assert response.status_code == 302 and response.url == reverse("admin:core_arenaclient_changelist")
        return ArenaClient.objects.get(username=username)

    def create_game(self, name: str, map_file_extension: str) -> Game:
        if Game.objects.filter(name=name).exists():
            raise Exception("That already exists!")

        url = reverse("admin:core_game_add")
        response = self.django_client.post(
            url,
            {
                "name": name,
                "map_file_extension": map_file_extension,
            },
        )

        # we should be redirected back to the changelist
        assert response.status_code == 302 and response.url == reverse("admin:core_game_changelist")
        return Game.objects.get(name=name)

    def create_gamemode(self, name: str, game_id: int) -> GameMode:
        if GameMode.objects.filter(name=name, game_id=game_id).exists():
            raise Exception("That already exists!")

        url = reverse("admin:core_gamemode_add")
        response = self.django_client.post(
            url,
            {
                "name": name,
                "game": game_id,
            },
        )

        # we should be redirected back to the changelist
        assert response.status_code == 302 and response.url == reverse("admin:core_gamemode_changelist")
        return GameMode.objects.get(name=name, game_id=game_id)

    def create_competition(
        self,
        name: str,
        game_mode_id: int,
        playable_race_ids=None,
        require_trusted_infrastructure=True,
        **kwargs,
    ) -> Competition:
        if playable_race_ids is None:
            playable_race_ids = {}
        if Competition.objects.filter(name=name).exists():
            raise Exception("That already exists!")

        url = reverse("admin:core_competition_add")
        response = self.django_client.post(
            url,
            {
                "name": name,
                "type": type,
                "game_mode": game_mode_id,
                "playable_races": playable_race_ids,
                "require_trusted_infrastructure": require_trusted_infrastructure,
                **kwargs,
            },
        )

        # we should be redirected back to the changelist
        assert response.status_code == 302 and response.url == reverse("admin:core_competition_changelist")
        return Competition.objects.get(name=name)

    def open_competition(self, competition_id: int):
        competition = Competition.objects.get(id=competition_id)
        url = reverse("admin:core_competition_change", args=(competition.pk,))
        data = {
            "_open-competition": "Open competition",
            "competition": competition_id,
            "name": competition.name,  # required by the form
            "game_mode": competition.game_mode_id,  # required by the form
            # if this isn't set here, it reverts to false - I don't understand why :(
            "indepth_bot_statistics_enabled": competition.indepth_bot_statistics_enabled,
        }
        response = self.django_client.post(url, data)

        # we should be redirected back to the same page
        assert response.status_code == 302 and response.url == "."

    def pause_competition(self, competition_id: int):
        competition = Competition.objects.get(id=competition_id)
        url = reverse("admin:core_competition_change", args=(competition.pk,))
        data = {
            "_pause-competition": "Pause competition",
            "competition": competition_id,
            "name": competition.name,  # required by the form
            "game_mode": competition.game_mode_id,  # required by the form
        }
        response = self.django_client.post(url, data)

        # we should be redirected back to the same page
        assert response.status_code == 302 and response.url == "."

    def close_competition(self, competition_id: int):
        competition = Competition.objects.get(id=competition_id)
        url = reverse("admin:core_competition_change", args=(competition.pk,))
        data = {
            "_close-competition": "Close competition",
            "competition": competition_id,
            "name": competition.name,  # required by the form
            "game_mode": competition.game_mode_id,  # required by the form
        }
        response = self.django_client.post(url, data)

        # we should be redirected back to the same page
        assert response.status_code == 302 and response.url == "."

    def cancel_matches(self, match_ids: list[int]):
        url = reverse("admin:core_match_changelist")
        data = {
            "action": ["cancel_matches"],
            "_selected_action": match_ids,
        }
        response = self.django_client.post(url, data)

        # we should be redirected back to the same page
        assert response.status_code == 302 and response.url == url

    def request_match(
        self,
        matchup_type: str,
        bot1: Bot,
        bot2: Bot,
        matchup_race: str,
        map_selection_type: str,
        map: Map,
        map_pool: MapPool,
        match_count: int,
    ) -> Match:
        url = reverse("requestmatch")
        data = {
            "matchup_type": matchup_type,
            "bot1": bot1.id,
            "bot2": bot2.id,
            "matchup_race": matchup_race,
            "map_selection_type": map_selection_type,
            "map": map.id if map is not None else "",
            "map_pool": map_pool.id if map_pool is not None else "",
            "match_count": match_count,
        }
        response = self.django_client.post(url, data)

        assert response.status_code == 302 and response.url == url
        return Match.objects.filter(requested_by=response.wsgi_request.user).order_by("-created").first()
