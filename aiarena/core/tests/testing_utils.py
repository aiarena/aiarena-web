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
from aiarena.core.models import User, Bot, Map, Match, Result, MatchParticipation, Season, Round, ArenaClient, \
    Season
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
                                                                     'owner': owner_id,
                                                                     'patreon_level': patreon_level})

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

    def create_competition(self, name: str, type: str, enabled: bool) -> Season:
        response = self.django_client.post('/admin/core/competition/add/', {'name': name,
                                                                            'type': type,
                                                                            'enabled': enabled, })

        assert response.status_code == 302  # redirect on success
        return Season.objects.get(name=name)

    def open_competition(self, competition_id: int):
        # The form needs certain details to be valid, so retrieve them
        competition = Season.objects.get(id=competition_id)
        response = self.django_client.post(f'/admin/core/competition/{competition}/change/', {
            '_open-season': 'Open season',
            'competition': competition.competition_id, })

        assert response.status_code == 302  # redirect on success

    def request_match(self):
        response = self.django_client.post(f'/api/arenaclient/matches/', self.get_api_headers())

        assert response.status_code == 302  # redirect on success
