from django.core.files import File
from django.test import Client

from aiarena.core.models import User, Bot, Match, Result, MatchParticipation, ArenaClient, \
    Competition
from aiarena.core.models.game import Game
from aiarena.core.models.game_type import GameMode


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
        competition = Competition.objects.get(id=competition_id)
        response = self.django_client.post(f'/admin/core/competition/{competition_id}/change/', {
            '_open-competition': 'Open competition',
            'competition': competition_id,
            'name': competition.name,  # required by the form
            'type': competition.type,  # required by the form
            'game_mode': competition.game_mode_id,  # required by the form
        })

        assert response.status_code == 302

    def request_match(self) -> Match:
        response = self.django_client.post(f'/api/arenaclient/matches/', self.get_api_headers())

        assert response.status_code == 201
        return Match.objects.get(id=response.data['id'])

