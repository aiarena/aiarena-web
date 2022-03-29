from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client
from django.urls import reverse

from rest_framework.authtoken.models import Token

from typing import List

from aiarena.core.models import User, Match, Result, ArenaClient, \
    Competition, Bot, Map, MapPool
from aiarena.core.models.game import Game
from aiarena.core.models.game_mode import GameMode
from aiarena.core.tests.tests import BaseTestMixin


class TestingClient:
    TEST_PASSWORD = 'x'

    def __init__(self, django_client=Client()):
        self.django_client = django_client
        self.api_token: str = None

    def login(self, user: User):
        self.django_client.force_login(user)

    def logout(self):
        self.django_client.logout()

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

        # we should be redirected back to the changelist
        assert response.status_code == 302 and response.url == reverse('admin:core_user_changelist')
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

        # we should be redirected back to the changelist
        assert response.status_code == 302 and response.url == reverse('admin:core_arenaclient_changelist')
        return ArenaClient.objects.get(username=username)

    def create_game(self, name: str) -> Game:
        if Game.objects.filter(name=name).exists():
            raise Exception('That already exists!')

        url = reverse('admin:core_game_add')
        response = self.django_client.post(url, {'name': name, })

        # we should be redirected back to the changelist
        assert response.status_code == 302 and response.url == reverse('admin:core_game_changelist'), f"{response.status_code}|{302} {response.url}|{reverse('admin:core_game_changelist')}"
        return Game.objects.get(name=name)

    def create_gamemode(self, name: str, game_id: int) -> GameMode:
        if GameMode.objects.filter(name=name, game_id=game_id).exists():
            raise Exception('That already exists!')

        url = reverse('admin:core_gamemode_add')
        response = self.django_client.post(url, {'name': name,
                                                 'game': game_id, })

        # we should be redirected back to the changelist
        assert response.status_code == 302 and response.url == reverse('admin:core_gamemode_changelist')
        return GameMode.objects.get(name=name, game_id=game_id)

    def create_competition(self, name: str, type: str, game_mode_id: int) -> Competition:
        if Competition.objects.filter(name=name).exists():
            raise Exception('That already exists!')

        url = reverse('admin:core_competition_add')
        response = self.django_client.post(url, {'name': name,
                                                 'type': type,
                                                 'game_mode': game_mode_id, })

        # we should be redirected back to the changelist
        assert response.status_code == 302 and response.url == reverse('admin:core_competition_changelist')
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

        # we should be redirected back to the same page
        assert response.status_code == 302 and response.url == '.'

    def pause_competition(self, competition_id: int):
        competition = Competition.objects.get(id=competition_id)
        url = reverse('admin:core_competition_change', args=(competition.pk,))
        data = {
            '_pause-competition': 'Pause competition',
            'competition': competition_id,
            'name': competition.name,  # required by the form
            'type': competition.type,  # required by the form
            'game_mode': competition.game_mode_id,  # required by the form
        }
        response = self.django_client.post(url, data)

        # we should be redirected back to the same page
        assert response.status_code == 302 and response.url == '.'

    def close_competition(self, competition_id: int):
        competition = Competition.objects.get(id=competition_id)
        url = reverse('admin:core_competition_change', args=(competition.pk,))
        data = {
            '_close-competition': 'Close competition',
            'competition': competition_id,
            'name': competition.name,  # required by the form
            'type': competition.type,  # required by the form
            'game_mode': competition.game_mode_id,  # required by the form
        }
        response = self.django_client.post(url, data)

        # we should be redirected back to the same page
        assert response.status_code == 302 and response.url == '.'

    def request_match(self,
                      matchup_type: str,
                      bot1: Bot,
                      bot2: Bot,
                      matchup_race: str,
                      map_selection_type: str,
                      map: Map,
                      map_pool: MapPool,
                      match_count: int) -> Match:
        url = reverse('requestmatch')
        data = {
                'matchup_type': matchup_type,
                'bot1'        : bot1.id,
                'bot2'        : bot2.id,
                'matchup_race': matchup_race,
                'map_selection_type': map_selection_type,
                'map'         : map.id if map is not None else '',
                'map_pool'    : map_pool.id if map_pool is not None else '',
                'match_count' : match_count,
        }
        response = self.django_client.post(url, data)

        assert response.status_code == 302 and response.url == url
        return Match.objects.filter(requested_by=response.wsgi_request.user).order_by('-created').first()

    def post_to_matches(self) -> Match:
        url = reverse('ac_next_match-list')
        response = self.django_client.post(url)
        return response

    def next_match(self) -> Match:
        response = self.post_to_matches()

        assert response.status_code == 201, f"{response.status_code} {response.data}"
        return Match.objects.get(id=response.data['id'])

    def cancel_matches(self, match_ids: List[int]):
        url = reverse('admin:core_match_changelist')
        data = {
            'action': ['cancel_matches'],
            '_selected_action': match_ids,
        }
        response = self.django_client.post(url, data)

        # we should be redirected back to the same page
        assert response.status_code == 302 and response.url == url

    def submit_custom_result(self, match_id, result_type, replay_file, bot1_data, bot2_data, bot1_log, bot2_log,
                                arenaclient_log, bot1_tags=None, bot2_tags=None):
        data = {
            'match': match_id,
            'type': result_type,
            'replay_file': replay_file,
            'game_steps': 500,
            'bot1_data': bot1_data,
            'bot2_data': bot2_data,
            'bot1_log': bot1_log,
            'bot2_log': bot2_log,
            'bot1_avg_step_time': 0.2,
            'bot2_avg_step_time': 0.1,
            'arenaclient_log': arenaclient_log,
        }
        if bot1_tags: data['bot1_tags'] = bot1_tags
        if bot2_tags: data['bot2_tags'] = bot2_tags
        return self.publish_result(data)

    def publish_result(self, data):
        url = reverse('ac_submit_result-list')
        return self.django_client.post(url,
                                        data=data)

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
                    'game_steps': 1234,
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
            response = self.publish_result(data)

            assert response.status_code == 201, f"{response.status_code} {response.data} {data}"
            return Result.objects.get(id=response.data['result_id'])
