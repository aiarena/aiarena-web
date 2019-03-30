import os

from django.core.files import File
from django.test import TestCase

from aiarena.core.models import User, Bot
from aiarena.core.utils import calculate_md5


class UtilsTestCase(TestCase):
    def test_calc_md5(self):
        filename = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'test_bot.zip')
        file = open(filename, 'rb')
        self.assertEqual('7411028ba931baaad47bf5810215e4f8', calculate_md5(file))


class UserTestCase(TestCase):
    def test_user_creation(self):
        User.objects.create(username='test user', email='test@test.com')


class BotTestCase(TestCase):
    def test_bot_creation(self):
        user = User.objects.create(username='test user', email='test@test.com')
        # For some reason using an absolute file path here for will cause it to mangle the save directory and fail
        # later whilst handling the bot_zip file save
        file = open('./aiarena/core/test_bot.zip', 'rb')
        bot = Bot.objects.create(user=user, name='test', bot_zip=File(file), plays_race='T', type='Python')
        self.assertEqual('7411028ba931baaad47bf5810215e4f8', bot.bot_zip_md5hash)
