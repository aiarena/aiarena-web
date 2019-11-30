from aiarena.core.models import Match, Round, Bot, User
from aiarena.core.tests import FullDataSetTestCase


class PageRenderTestCase(FullDataSetTestCase):
    """
    Tests to ensure website pages don't break.
    """

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
        active_bot = Bot.objects.filter(active=True)[0]
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

        # ranking
        response = self.client.get('/ranking/')
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
