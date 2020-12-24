from datetime import datetime
import os
from datetime import timedelta
from io import StringIO

from constance import config
from django.core.exceptions import ValidationError
from django.core.files import File
from django.core.files.uploadedfile import SimpleUploadedFile
from django.core.management import call_command, CommandError
from django.test import TestCase, TransactionTestCase, Client
from django.utils import timezone

from aiarena.core.api import Matches
from aiarena.core.management.commands import cleanupreplays
from aiarena.core.models import User, Bot, Map, Match, Result, MatchParticipation, Competition, Round, ArenaClient, \
    Competition
from aiarena.core.models.game import Game
from aiarena.core.models.game_type import GameMode
from aiarena.core.utils import calculate_md5


class TestingClient:
    TEST_PASSWORD = 'x'

    def __init__(self):
        self.django_client = Client()
        self.api_token: str = None

    def login_as(self, user: User):
        self.django_client.force_login(user)

    def set_api_token(self, api_token: str):
        self.api_token = api_token

    def get_api_headers(self) -> dict:
        return {"Authorization": f"Token {self.api_token}"}


    def create_user(self,
                    username: str,
                    password: str,
                    email: str,
                    type: str,
                    owner_id: int,
                    patreon_level: str = 'none') -> User:
        response = self.django_client.post('/admin/core/user/add/', {'username': username,
                                                                     'password': password,
                                                                     'email': email,
                                                                     'type': type,
                                                                     'owner': owner_id,})

        assert response.status_code == 302  # redirect on success
        return User.objects.get(username=username)

    def create_arenaclient(self, username: str, email: str, owner_id: int) -> ArenaClient:
        response = self.django_client.post('/admin/core/arenaclient/add/', {'username': username,
                                                                            'email': email,
                                                                            'password': self.TEST_PASSWORD,
                                                                            'type': 'ARENA_CLIENT',
                                                                            'owner': owner_id, })

        assert response.status_code == 302  # redirect on success
        return ArenaClient.objects.get(username=username)

    def create_game(self, name: str) -> Game:
        response = self.django_client.post('/admin/core/game/add/', {'name': name,})

        assert response.status_code == 302
        return Game.objects.get(name=name)

    def create_gamemode(self, name: str, game_id: int) -> GameMode:
        response = self.django_client.post('/admin/core/gamemode/add/', {'name': name,
                                                                         'game': game_id,})

        assert response.status_code == 302
        return GameMode.objects.get(name=name, game_id=game_id)

    def create_competition(self, name: str, type: str, game_mode_id: int) -> Competition:
        response = self.django_client.post('/admin/core/competition/add/', {'name': name,
                                                                            'type': type,
                                                                            'game_mode': game_mode_id, })

        assert response.status_code == 302  # redirect on success
        return Competition.objects.get(name=name)

    def open_competition(self, competition_id: int):
        response = self.django_client.post(f'/admin/core/competition/{competition_id}/change/', {
            '_open-competition': 'Open competition',
            'competition': competition_id, })

        assert response.status_code == 302  # redirect on success

    def request_match(self):
        response = self.django_client.post(f'/api/arenaclient/matches/', self.get_api_headers())

        assert response.status_code == 302  # redirect on success
