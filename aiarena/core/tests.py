import os

from django.core.files import File
from django.test import TestCase

from aiarena.core.models import User, Bot, Map
from aiarena.core.utils import calculate_md5


class BaseTestCase(TestCase):
    # For some reason using an absolute file path here will cause it to mangle the save directory and fail
    # later whilst handling the bot_zip file save
    test_bot_zip = open('./aiarena/core/test_bot.zip', 'rb')

    def _create_bot(self, name):
        return Bot.objects.create(user=self.staffUser, name=name, bot_zip=File(self.test_bot_zip))

    def _create_active_bot(self, name):
        return Bot.objects.create(user=self.staffUser, name=name, bot_zip=File(self.test_bot_zip), active=True)


class LoggedInTestCase(BaseTestCase):
    def setUp(self):
        self.staffUser = User.objects.create_user(username='staff_user', password='x', email='staff_user@aiarena.net',
                                                  is_staff=True)
        self.regularUser = User.objects.create_user(username='regular_user', password='x',
                                                    email='regular_user@aiarena.net')


class MatchReadyTestCase(LoggedInTestCase):
    def setUp(self):
        super(MatchReadyTestCase, self).setUp()

        self.regularUserBot1 = Bot.objects.create(user=self.regularUser, name='regularUserBot1', active=False,
                                                  bot_zip=File(self.test_bot_zip), plays_race='T', type='Python')

        self.regularUserBot2 = Bot.objects.create(user=self.regularUser, name='regularUserBot2', active=False,
                                                  bot_zip=File(self.test_bot_zip), plays_race='Z', type='Python')

        self.staffUserBot1 = Bot.objects.create(user=self.staffUser, name='staffUserBot1', active=False,
                                                bot_zip=File(self.test_bot_zip), plays_race='P', type='Python')

        self.staffUserBot2 = Bot.objects.create(user=self.staffUser, name='staffUserBot2', active=False,
                                                bot_zip=File(self.test_bot_zip), plays_race='R', type='Python')
        Map.objects.create(name='testmap')


# User this to pre-build a full dataset for testing
class FullDataSetTestCase(MatchReadyTestCase):
    def setUp(self):
        super(FullDataSetTestCase, self).setUp()
        # todo: generate some matches and results


class UtilsTestCase(BaseTestCase):
    def test_calc_md5(self):
        filename = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'test_bot.zip')
        file = open(filename, 'rb')
        self.assertEqual('7411028ba931baaad47bf5810215e4f8', calculate_md5(file))


class UserTestCase(BaseTestCase):
    def test_user_creation(self):
        User.objects.create(username='test user', email='test@test.com')


class BotTestCase(BaseTestCase):
    def test_bot_creation(self):
        user = User.objects.create(username='test user', email='test@test.com')
        bot = Bot.objects.create(user=user, name='test', bot_zip=File(self.test_bot_zip), plays_race='T', type='Python')
        self.assertEqual('7411028ba931baaad47bf5810215e4f8', bot.bot_zip_md5hash)

        # check the bot file now exists
        self.assertTrue(os.path.isfile('./private-media/bots/{0}/bot_zip'.format(bot.id)))

        # todo: check file overwrite functionality


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

    def test_get_bot_page(self):
        response = self.client.get('/bots/{0}/'.format(self.regularUserBot1.id))
        self.assertEqual(response.status_code, 200)

    def test_get_author_page(self):
        response = self.client.get('/authors/')
        self.assertEqual(response.status_code, 200)

    def test_get_authors_page(self):
        response = self.client.get('/authors/{0}/'.format(self.regularUser.id))
        self.assertEqual(response.status_code, 200)

    def test_get_ranking_page(self):
        response = self.client.get('/ranking/')
        self.assertEqual(response.status_code, 200)

    def test_get_results_page(self):
        response = self.client.get('/results/')
        self.assertEqual(response.status_code, 200)

    def test_get_rules_page(self):
        response = self.client.get('/rules/')
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


class PrivateStorageTestCase(MatchReadyTestCase):
    pass  # todo
