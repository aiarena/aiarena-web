from aiarena.core.utils import TestCase
from aiarena.core.tests.tests import LoggedInMixin


class StreamTestCase(LoggedInMixin, TestCase):

    def test_stream_nextreplay(self):
        self.client.login(username='regular_user', password='x')
        response = self.client.get('/api/stream/next-replay/')
        self.assertEqual(response.status_code, 403)

        self.client.login(username='staff_user', password='x')
        response = self.client.get('/api/stream/next-replay/')
        self.assertEqual(response.status_code, 200)
