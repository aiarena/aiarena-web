from django.test import TestCase

from aiarena.core.models import *


class AuthorisedMatchTestCase(TestCase):
    def setUp(self):
        user = User.objects.create_user(username='test', password='x', is_superuser=True)
        self.client.login(username='test', password='x')

    def test_next_match_no_maps(self):
        # not having any maps should cause this to fall over
        response = self.client.get('/api/matches/next/')
        self.assertEqual(response.status_code, 500)

    def test_next_match_no_bots(self):
        Map.objects.create(name='testmap')
        # not having any bots should cause this to fall over
        response = self.client.get('/api/matches/next/')
        self.assertEqual(response.status_code, 500)
