from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client
from django.urls import reverse
from typing import List

from aiarena.core.models import User, Match, Result, ArenaClient, \
    Competition
from aiarena.core.models.game import Game
from aiarena.core.models.game_type import GameMode
from aiarena.core.tests.tests import BaseTestMixin


class TestingClient:
    TEST_PASSWORD = 'x'

    def __init__(self, django_client=Client()):
        self.django_client = django_client
        self.api_token: str = None

    def login(self, user: User):
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
                    owner_id: int) -> User:
        if User.objects.filter(username=username).exists():
            raise Exception('That already exists!')

        url = reverse('admin:core_user_add')
        response = self.django_client.post(url, {'username': username,
                                                 'password': password,
                                                 'email': email,
                                                 'type': type,
                                                 'owner': owner_id, })

        assert response.status_code == 302  # redirect on success
        return User.objects.get(username=username)

    def create_arenaclient(self, username: str, email: str, owner_id: int) -> ArenaClient:
        if ArenaClient.objects.filter(username=username).exists():
            raise Exception('That already exists!')

        url = reverse('admin:core_arenaclient_add')
        response = self.django_client.post(url, {'username': username,
                                                 'email': email,
                                                 'password': self.TEST_PASSWORD,
                                                 'type': 'ARENA_CLIENT',
                                                 'owner': owner_id, })

        assert response.status_code == 302  # redirect on success
        return ArenaClient.objects.get(username=username)

    def create_game(self, name: str) -> Game:
        if Game.objects.filter(name=name).exists():
            raise Exception('That already exists!')

        url = reverse('admin:core_game_add')
        response = self.django_client.post(url, {'name': name, })

        assert response.status_code == 302
        return Game.objects.get(name=name)

    def create_gamemode(self, name: str, game_id: int) -> GameMode:
        if GameMode.objects.filter(name=name, game_id=game_id).exists():
            raise Exception('That already exists!')

        url = reverse('admin:core_gamemode_add')
        response = self.django_client.post(url, {'name': name,
                                                 'game': game_id, })

        assert response.status_code == 302
        return GameMode.objects.get(name=name, game_id=game_id)

    def create_competition(self, name: str, type: str, game_mode_id: int) -> Competition:
        if Competition.objects.filter(name=name).exists():
            raise Exception('That already exists!')

        url = reverse('admin:core_competition_add')
        response = self.django_client.post(url, {'name': name,
                                                 'type': type,
                                                 'game_mode': game_mode_id, })

        assert response.status_code == 302  # redirect on success
        return Competition.objects.get(name=name)

    def open_competition(self, competition_id: int):
        competition = Competition.objects.get(id=competition_id)
        url = reverse('admin:core_competition_change', args=(competition.pk,))
        data = {
            '_open-competition': 'Open competition',
            'competition': competition_id,
            'name': competition.name,  # required by the form
            'type': competition.type,  # required by the form
            'game_mode': competition.game_mode_id,  # required by the form
        }
        response = self.django_client.post(url, data)

        assert response.status_code == 302

    def request_match(self) -> Match:
        url = reverse('ac_next_match-list')
        response = self.django_client.post(url, self.get_api_headers())

        assert response.status_code == 201
        return Match.objects.get(id=response.data['id'])

    def submit_result(self, match_id: int, type: str) -> Result:
        with open(BaseTestMixin.test_replay_path, 'rb') as replay_file, \
                open(BaseTestMixin.test_arenaclient_log_path, 'rb') as arenaclient_log, \
                open(BaseTestMixin.test_bot_datas['bot1'][0]['path'], 'rb') as bot1_data, \
                open(BaseTestMixin.test_bot_datas['bot2'][0]['path'], 'rb') as bot2_data, \
                open(BaseTestMixin.test_bot1_match_log_path, 'rb') as bot1_log, \
                open(BaseTestMixin.test_bot2_match_log_path, 'rb') as bot2_log:
            data = {'match': match_id,
                    'type': type,
                    'replay_file': SimpleUploadedFile("replay_file.SC2Replay",
                                                      replay_file.read()),
                    'game_steps': '1234',
                    'arenaclient_log': SimpleUploadedFile("arenaclient_log.log",
                                                          arenaclient_log.read()),
                    'bot1_data': SimpleUploadedFile("bot1_data.log",
                                                    bot1_data.read()),
                    'bot2_data': SimpleUploadedFile("bot2_data.log",
                                                    bot2_data.read()),
                    'bot1_log': SimpleUploadedFile("bot1_log.log",
                                                   bot1_log.read()),
                    'bot2_log': SimpleUploadedFile("bot2_log.log",
                                                   bot2_log.read()),
                    'bot1_avg_step_time': '0.111',
                    'bot2_avg_step_time': '0.222', }
            url = reverse('ac_submit_result-list')
            response = self.django_client.post(url,
                                               data,
                                               **self.get_api_headers())

            assert response.status_code == 201
            return Result.objects.get(id=response.data['result_id'])
