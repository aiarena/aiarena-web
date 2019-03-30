import os

from django.test import TestCase

from aiarena.core.models import User
from aiarena.core.utils import calculate_md5


class UtilsTestCase(TestCase):
    def test_calc_md5(self):
        filename = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'test_bot.zip')
        file = open(filename, 'rb')
        self.assertEqual('7411028ba931baaad47bf5810215e4f8', calculate_md5(file))


class UserTestCase(TestCase):
    def test_user_creation(self):
        User.objects.create(username='test user', email='test@test.com')
