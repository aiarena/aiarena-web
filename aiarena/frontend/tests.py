from django.test import TransactionTestCase, TestCase
from django.urls.base import reverse
from aiarena.core.models import Match, Round, Bot, User, Result, Competition
from aiarena.core.tests.tests import FullDataSetMixin
from aiarena.core.tests.testing_utils import TestingClient

from django_fakeredis import FakeRedis

class AdminMethodsTestCase(FullDataSetMixin, TestCase):

    @FakeRedis("django_redis.get_redis_connection")
    def setUp(self):
        super().setUp()
        # all tests need us logged in as staff
        self.test_client.login(self.staffUser1)

    @FakeRedis("django_redis.get_redis_connection")
    def test_admin_match_cancelling(self):
        matches = Match.objects.filter(result__isnull=True)
        match_ids = [match.id for match in matches]
        self.test_client.cancel_matches(match_ids)
        for match in matches:
            result = Result.objects.get(match=match)
            self.assertTrue(result.type == "MatchCancelled",
                            msg=f"failed to Cancel Match<{match}>, Result<{result}> Using the admin interface ")

    @FakeRedis("django_redis.get_redis_connection")
    def test_admin_competition_statuses(self):
        competition = Competition.objects.first()
        self.assertEqual(competition.status, 'open', msg=f"first competition in the test database is not open!")

        self.test_client.pause_competition(competition.id)
        competition = Competition.objects.first()
        self.assertEqual(competition.status, 'paused',
                         msg=f"failed responsechange<pause> on Competition<{competition}> Using the admin interface ")

        self.test_client.open_competition(competition.id)
        competition.refresh_from_db()
        self.assertEqual(competition.status, 'open',
                         msg=f"failed responsechange<open> on Competition<{competition}> Using the admin interface ")

        self.test_client.close_competition(competition.id)
        competition.refresh_from_db()
        self.assertEqual(competition.status, 'closing',
                         msg=f"failed responsechange<closing> on Competition<{competition}> Using the admin interface ")


class PageRenderTestCase(FullDataSetMixin, TransactionTestCase):
    """
    Tests to ensure website pages don't break.
    """

    @FakeRedis("django_redis.get_redis_connection")
    def test_render_pages(self):
        # index
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)

        # login
        response = self.client.get('/accounts/login/')
        self.assertEqual(response.status_code, 200)

        # register
        response = self.client.get('/accounts/register/')
        self.assertEqual(response.status_code, 200)

        # bots
        response = self.client.get('/bots/')
        self.assertEqual(response.status_code, 200)

        # profile before login - should redirect
        response = self.client.get('/profile/')
        self.assertEqual(response.status_code, 302)

        # bot
        active_bot = Bot.objects.filter(competition_participations__active=True)[0]
        response = self.client.get('/bots/{0}/'.format(active_bot.id))
        self.assertEqual(response.status_code, 200)

        # bot edit
        self.client.login(username='regular_user1', password='x')
        # test bot edit pages we can access
        bots = Bot.objects.filter(user=self.regularUser1)
        for bot in bots:
            response = self.client.get('/bots/{0}/edit/'.format(bot.pk))
            self.assertEqual(response.status_code, 200)

        # test bot edit pages we can't access
        bots = Bot.objects.exclude(user=self.regularUser1)
        for bot in bots:
            response = self.client.get('/bots/{0}/edit/'.format(bot.pk))
            self.assertEqual(response.status_code, 404)

        # authors
        response = self.client.get('/authors/')
        self.assertEqual(response.status_code, 200)

        # author
        response = self.client.get('/authors/{0}/'.format(self.regularUser1.id))
        self.assertEqual(response.status_code, 200)

        # match
        response = self.client.get('/matches/{0}/'.format(Match.objects.all()[0].id))
        self.assertEqual(response.status_code, 200)

        # results
        response = self.client.get('/results/')
        self.assertEqual(response.status_code, 200)

        # password_reset
        response = self.client.get('/accounts/password_reset/')
        self.assertEqual(response.status_code, 200)

        # stream
        response = self.client.get('/stream/')
        self.assertEqual(response.status_code, 200)

        # match-queue
        response = self.client.get('/match-queue/')
        self.assertEqual(response.status_code, 200)

        # round
        response = self.client.get('/rounds/{0}/'.format(Round.objects.all()[0].id))
        self.assertEqual(response.status_code, 200)

        # arenaclients
        response = self.client.get('/arenaclients/')
        self.assertEqual(response.status_code, 200)

        # arenaclients
        for arenaclient in User.objects.filter(type='ARENA_CLIENT'):
            response = self.client.get('/arenaclients/{0}/'.format(arenaclient.id))
            self.assertEqual(response.status_code, 200)

        # profile
        response = self.client.get('/profile/')
        self.assertEqual(response.status_code, 200)

        # token
        response = self.client.get('/profile/token/')
        self.assertEqual(response.status_code, 200)

        # recreate - will redirect
        response = self.client.post('/profile/token/')
        self.assertEqual(response.status_code, 302)

        # requestmatch
        response = self.client.get('/requestmatch/')
        self.assertEqual(response.status_code, 200)


class RequestMatchTestCase(FullDataSetMixin, TestCase):

    @FakeRedis("django_redis.get_redis_connection")
    def setUp(self):
        super().setUp()
        self.client = TestingClient()

    @FakeRedis("django_redis.get_redis_connection")
    def test_request_match_regular_user(self) -> Match:

        # log in as a regular user
        self.user = self.regularUser1
        url = reverse('requestmatch')
        data = {
                'matchup_type': 'specific_matchup',
                'bot1'        : 1,
                'bot2'        : 3,
                'matchup_race': 'any',
                'map'         : 1,
                'match_count' : 1,
        }

        assert self.client.django_client.post(url,data).status_code == 302, f"{self.client.django_client.post(url,data).status_code}"
