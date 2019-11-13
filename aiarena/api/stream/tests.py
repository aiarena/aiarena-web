from aiarena.core.tests import LoggedInTestCase


class StreamTestCase(LoggedInTestCase):
    def setUp(self):
        super().setUp()

    def test_stream_nextreplay(self):
        self.client.login(username='regular_user', password='x')
        response = self.client.get('/api/stream/next-replay/')
        self.assertEqual(response.status_code, 403)

        self.client.login(username='staff_user', password='x')
        response = self.client.get('/api/stream/next-replay/')
        self.assertEqual(response.status_code, 200)
