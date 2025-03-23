from django.test import TransactionTestCase

from aiarena.core.models import User
from aiarena.core.tests.test_mixins import LoggedInMixin


class SetStatusTestCase(LoggedInMixin, TransactionTestCase):
    def setUp(self):
        super().setUp()
        self.client.force_login(User.objects.get(username="arenaclient1"))

    def test_set_status(self):
        return self.client.post("/api/arenaclient/set-status/", {"status": "idle"})
