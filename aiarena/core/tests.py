from django.test import TestCase

from aiarena.core.models import *


class UserTestCase(TestCase):
    def test_user_creation(self):
        User.objects.create(username='test user', email='test@test.com')
