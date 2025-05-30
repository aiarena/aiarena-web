import io
import zipfile

from django.core.files.uploadedfile import SimpleUploadedFile

import pytest

from aiarena.core.models import Bot, Competition, CompetitionParticipation, Game, GameMode, Map, MapPool, WebsiteUser
from aiarena.core.models.bot_race import BotRace
from aiarena.core.tests.base import BrowserHelper


@pytest.fixture
def get_fixture(request: pytest.FixtureRequest):
    """
    Fixture that can be used to get another fixture by name and automatically calls it if it's a callable.
    Useful if you want to parameterize the test with fixtures, since pytest
    does not allow this.
    https://github.com/pytest-dev/pytest/issues/349#issuecomment-471400399

    Example:

        @pytest.mark.parametrize('name', ('fixture_1', 'fixture_2'))
        def test_integration(get_fixture, name):
            parametrized_fixture = get_fixture(name)
            ...

    """

    def check_and_call_if_callable(name: str):
        fixture = request.getfixturevalue(name)
        return fixture() if callable(fixture) else fixture

    return check_and_call_if_callable


@pytest.fixture
def cpp_win_zip_file():
    def _make_zip():
        buffer = io.BytesIO()
        with zipfile.ZipFile(buffer, mode="w", compression=zipfile.ZIP_DEFLATED) as zf:
            zf.writestr("a_cpp_win_bot.exe", b'int main() { printf("12 Pool\\n"); return 0; }')
        buffer.seek(0)
        return SimpleUploadedFile("bot.zip", buffer.read(), content_type="application/zip")

    return _make_zip


@pytest.fixture
def cpp_lin_zip_file():
    def _make_zip():
        buffer = io.BytesIO()
        with zipfile.ZipFile(buffer, mode="w", compression=zipfile.ZIP_DEFLATED) as zf:
            zf.writestr("a_cpp_lin_bot", b'int main() { printf("12 Pool\\n"); return 0; }')
        buffer.seek(0)
        return SimpleUploadedFile("bot.zip", buffer.read(), content_type="application/zip")

    return _make_zip


@pytest.fixture
def dotnet_zip_file():
    def _make_zip():
        buffer = io.BytesIO()
        with zipfile.ZipFile(buffer, mode="w", compression=zipfile.ZIP_DEFLATED) as zf:
            zf.writestr(
                "a_dot_net_bot.dll", b'using System; class Bot { static void Main() { Console.WriteLine("12 Pool"); } }'
            )
        buffer.seek(0)
        return SimpleUploadedFile("bot.zip", buffer.read(), content_type="application/zip")

    return _make_zip


@pytest.fixture
def java_zip_file():
    def _make_zip():
        buffer = io.BytesIO()
        with zipfile.ZipFile(buffer, mode="w", compression=zipfile.ZIP_DEFLATED) as zf:
            zf.writestr(
                "a_java_bot.jar",
                b'public class Bot { public static void main(String[] args) { System.out.println("12 Pool"); } }',
            )
        buffer.seek(0)
        return SimpleUploadedFile("bot.zip", buffer.read(), content_type="application/zip")

    return _make_zip


@pytest.fixture
def node_js_zip_file():
    def _make_zip():
        buffer = io.BytesIO()
        with zipfile.ZipFile(buffer, mode="w", compression=zipfile.ZIP_DEFLATED) as zf:
            zf.writestr("a_node_js_bot.js", b'console.log("12 Pool");')
        buffer.seek(0)
        return SimpleUploadedFile("bot.zip", buffer.read(), content_type="application/zip")

    return _make_zip


@pytest.fixture
def python_zip_file():
    def _make_zip():
        buffer = io.BytesIO()
        with zipfile.ZipFile(buffer, mode="w", compression=zipfile.ZIP_DEFLATED) as zf:
            zf.writestr("run.py", b'print("12 Pool")')
        buffer.seek(0)
        return SimpleUploadedFile("bot.zip", buffer.read(), content_type="application/zip")

    return _make_zip


@pytest.fixture
def invalid_python_zip_file():
    def _make_zip():
        buffer = io.BytesIO()
        with zipfile.ZipFile(buffer, mode="w", compression=zipfile.ZIP_DEFLATED) as zf:
            zf.writestr("notrun.py", b'print("12 Pool")')
        buffer.seek(0)
        return SimpleUploadedFile("bot.zip", buffer.read(), content_type="application/zip")

    return _make_zip


@pytest.fixture
def all_bot_races(db):
    BotRace.create_all_races()


@pytest.fixture
def bh(live_server, transactional_db):
    browser_helper = BrowserHelper(live_server=live_server)
    return browser_helper


@pytest.fixture
def admin_user(db):
    return WebsiteUser.objects.create_superuser(
        username="george",
        email="george@aiarena.net",
        password="guest",
    )


@pytest.fixture
def user(db):
    return WebsiteUser.objects.create_user(
        username="billy",
        email="billy@example.com",
        password="guest",
    )


@pytest.fixture
def other_user(db):
    return WebsiteUser.objects.create_user(
        username="bobby",
        email="bobby@example.com",
        password="guest",
    )


@pytest.fixture
def bot(db, user, all_bot_races, python_zip_file):
    return Bot.objects.create(
        user=user,
        name="My_Bot",
        bot_zip_publicly_downloadable=False,
        bot_data_enabled=False,
        bot_data_publicly_downloadable=False,
        bot_zip=python_zip_file(),
        type="python",
        plays_race=BotRace.terran(),
    )


@pytest.fixture
def other_bot(db, other_user, python_zip_file):
    return Bot.objects.create(
        user=other_user,
        name="Not_My_Bot",
        bot_zip_publicly_downloadable=False,
        bot_data_enabled=False,
        bot_data_publicly_downloadable=False,
        bot_zip=python_zip_file(),
        type="python",
        plays_race=BotRace.zerg(),
    )


@pytest.fixture
def bot_factory():
    def create_bot(
        user,
        name,
        bot_zip_publicly_downloadable=False,
        bot_data_enabled=False,
        bot_data_publicly_downloadable=False,
        plays_race=BotRace.random(),
    ):
        return Bot.objects.create(
            user=user,
            name=name,
            bot_zip_publicly_downloadable=bot_zip_publicly_downloadable,
            bot_data_enabled=bot_data_enabled,
            bot_data_publicly_downloadable=bot_data_publicly_downloadable,
            plays_race=plays_race,
        )

    return create_bot


@pytest.fixture
def game(db):
    return Game.objects.create(
        name="Starcraft 2",
    )


@pytest.fixture
def game_mode(db, game):
    return GameMode.objects.create(
        name="melee",
        game=game,
    )


@pytest.fixture
def competition(db, game_mode):
    return Competition.objects.create(
        name="AI Arena SC2 Grand Prix",
        game_mode=game_mode,
    )


@pytest.fixture
def competition_factory(game_mode):
    def create_competition(name, game_mode, status):
        return Competition.objects.create(name=name, game_mode=game_mode, status=status)

    return create_competition


@pytest.fixture
def competition_participation_user(db, competition, bot):
    return CompetitionParticipation.objects.create(
        competition=competition,
        bot=bot,
    )


@pytest.fixture
def competition_participation_other_user(db, competition, other_bot):
    return CompetitionParticipation.objects.create(
        competition=competition,
        bot=other_bot,
    )


@pytest.fixture
def map(db, game_mode):
    return Map.objects.create(
        name="AiArenaArena513LE",
        file="/maps/AiArenaArena513LE.map",
        game_mode=game_mode,
    )


@pytest.fixture
def map_pool(db, map):
    map_pool = MapPool.objects.create(name="The Finest SC2 Maps")
    map_pool.maps.add(map)
    return map_pool
