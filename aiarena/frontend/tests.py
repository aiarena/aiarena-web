from aiarena.core.models import Match, Round, Bot
from aiarena.core.tests import FullDataSetTestCase


class PageRenderTestCase(FullDataSetTestCase):
    """
    Tests to ensure website pages don't break.
    """

    def test_get_index_page(self):
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)

    def test_get_bots_page(self):
        response = self.client.get('/bots/')
        self.assertEqual(response.status_code, 200)

    def test_get_bot_page_active(self):
        active_bot = Bot.objects.filter(active=True)[0]
        response = self.client.get('/bots/{0}/'.format(active_bot.id))
        self.assertEqual(response.status_code, 200)

    def test_get_bot_page_inactive(self):
        inactive_bot = Bot.objects.filter(active=False)[0]
        response = self.client.get('/bots/{0}/'.format(inactive_bot.id))
        self.assertEqual(response.status_code, 200)

    def test_get_bot_edit_page(self):
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

    def test_get_authors_page(self):
        response = self.client.get('/authors/')
        self.assertEqual(response.status_code, 200)

    def test_get_author_page(self):
        response = self.client.get('/authors/{0}/'.format(self.regularUser1.id))
        self.assertEqual(response.status_code, 200)

    def test_get_match_page(self):
        response = self.client.get('/matches/{0}/'.format(Match.objects.all()[0].id))
        self.assertEqual(response.status_code, 200)

    def test_get_ranking_page(self):
        response = self.client.get('/ranking/')
        self.assertEqual(response.status_code, 200)

    def test_get_results_page(self):
        response = self.client.get('/results/')
        self.assertEqual(response.status_code, 200)

    def test_get_login_page(self):
        response = self.client.get('/accounts/login/')
        self.assertEqual(response.status_code, 200)

    def test_get_register_page(self):
        response = self.client.get('/accounts/register/')
        self.assertEqual(response.status_code, 200)

    def test_get_reset_password_page(self):
        response = self.client.get('/accounts/password_reset/')
        self.assertEqual(response.status_code, 200)

    def test_get_stream_page(self):
        response = self.client.get('/stream/')
        self.assertEqual(response.status_code, 200)

    def test_get_match_queue_page(self):
        response = self.client.get('/match-queue/')
        self.assertEqual(response.status_code, 200)

    def test_get_round_page(self):
        response = self.client.get('/rounds/{0}/'.format(Round.objects.all()[0].id))
        self.assertEqual(response.status_code, 200)
