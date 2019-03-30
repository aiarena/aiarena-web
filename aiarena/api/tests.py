import os

from django.test import TestCase

from aiarena.core.models import *


class LoggedInTestCase(TestCase):
    def setUp(self):
        self.staffUser = User.objects.create_user(username='staff_user', password='x', email='staff_user@aiarena.net',
                                                  is_staff=True)
        self.regularUser = User.objects.create_user(username='regular_user', password='x',
                                                    email='regular_user@aiarena.net')


class MatchesTestCase(LoggedInTestCase):

    def test_next_match_not_authorized(self):
        response = self.client.get('/api/matches/next/')
        self.assertEqual(response.status_code, 403)

        self.client.login(username='regular_user', password='x')
        response = self.client.get('/api/matches/next/')
        self.assertEqual(response.status_code, 403)

    def test_next_match(self):
        self.client.login(username='staff_user', password='x')

        # no maps
        response = self.client.get('/api/matches/next/')
        self.assertEqual(response.status_code, 500)

        # not enough active bots
        Map.objects.create(name='testmap')
        response = self.client.get('/api/matches/next/')
        self.assertEqual(response.status_code, 500)

        # not enough active bots
        bot1 = Bot.objects.create(user=self.staffUser, name='testbot1')
        response = self.client.get('/api/matches/next/')
        self.assertEqual(response.status_code, 500)

        # not enough active bots
        bot2 = Bot.objects.create(user=self.regularUser, name='testbot2')
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


class ResultsTestCase(LoggedInTestCase):
    def test_create_result_not_authorized(self):
        response = self.client.get('/api/results/')
        self.assertEqual(response.status_code, 403)

        self.client.login(username='regular_user', password='x')
        response = self.client.get('/api/results/')
        self.assertEqual(response.status_code, 403)

    def CreateMatch(self):
        Map.objects.create(name='testmap')
        bot1 = Bot.objects.create(user=self.regularUser, name='testbot1', active=True)
        bot2 = Bot.objects.create(user=self.staffUser, name='testbot2', active=True)
        response = self.client.get('/api/matches/next/')
        self.assertEqual(response.status_code, 200)
        return response.data, bot1, bot2

    def PostResult(self, match, winner):
        filename = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'testReplay.SC2Replay')
        with open(filename) as replayFile:
            return self.client.post('/api/results/',
                                        {'match': match["id"],
                                         'winner': winner.id,
                                         'type': 'P1W',
                                         'replay_file': replayFile})

    def test_create_result(self):
        self.client.login(username='staff_user', password='x')

        match, bot1, bot2 = self.CreateMatch()

        response = self.PostResult(match, bot1)
        self.assertEqual(response.status_code, 201)
