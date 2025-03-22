import pytest

from aiarena.core.models import Bot, Competition, Game, GameMode, WebsiteUser
from aiarena.core.models.bot_race import BotRace
from aiarena.core.tests.base import BrowserHelper


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
def bot(db, user, all_bot_races):
    return Bot.objects.create(
        user=user,
        name="My Bot",
        bot_zip_publicly_downloadable=False,
        bot_data_enabled=False,
        bot_data_publicly_downloadable=False,
        plays_race=BotRace.terran(),
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
