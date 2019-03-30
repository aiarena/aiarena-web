from django.test import TestCase

from aiarena.core.models import *


class AuthorisedMatchTestCase(TestCase):
    def setUp(self):
        self.testUser = User.objects.create_user(username='test', password='x', is_superuser=True)
        self.client.login(username='test', password='x')

    def test_next_match(self):
        # no maps
        response = self.client.get('/api/matches/next/')
        self.assertEqual(response.status_code, 500)

        # not enough active bots
        Map.objects.create(name='testmap')
        response = self.client.get('/api/matches/next/')
        self.assertEqual(response.status_code, 500)

        # not enough active bots
        bot1 = Bot.objects.create(user=self.testUser, name='testbot1')
        response = self.client.get('/api/matches/next/')
        self.assertEqual(response.status_code, 500)

        # not enough active bots
        bot2 = Bot.objects.create(user=self.testUser, name='testbot2')
        response = self.client.get('/api/matches/next/')
        self.assertEqual(response.status_code, 500)

        # not enough active bots
        bot1.active = True
        bot1.save()
        response = self.client.get('/api/matches/next/')
        self.assertEqual(response.status_code, 500)

        # success
        bot2.active = True
        bot2.save()
        response = self.client.get('/api/matches/next/')
        self.assertEqual(response.status_code, 200)

        # ensure only 1 match was created
        self.assertEqual(Match.objects.count(), 1)
