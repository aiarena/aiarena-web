import io
import zipfile

from django.core.files.uploadedfile import SimpleUploadedFile

import pytest

from aiarena.core.models import Bot, Competition, CompetitionParticipation, Game, GameMode, Map, MapPool, WebsiteUser
from aiarena.core.models.bot_race import BotRace
from aiarena.core.tests.base import BrowserHelper


@pytest.fixture
def zip_file():
    buffer = io.BytesIO()
    with zipfile.ZipFile(buffer, mode="w", compression=zipfile.ZIP_DEFLATED) as zf:
        zf.writestr("run.py", b'print("12 Pool")')
    buffer.seek(0)
    return SimpleUploadedFile("bot.zip", buffer.read(), content_type="application/zip")


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
def bot(db, user, all_bot_races, zip_file):
    return Bot.objects.create(
        user=user,
        name="My_Bot",
        bot_zip_publicly_downloadable=False,
        bot_data_enabled=False,
        bot_data_publicly_downloadable=False,
        bot_zip=zip_file,
        type="python",
        plays_race=BotRace.terran(),
    )


@pytest.fixture
def other_bot(db, other_user, zip_file):
    return Bot.objects.create(
        user=other_user,
        name="Not_My_Bot",
        bot_zip_publicly_downloadable=False,
        bot_data_enabled=False,
        bot_data_publicly_downloadable=False,
        bot_zip=zip_file,
        type="python",
        plays_race=BotRace.zerg(),
    )


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
