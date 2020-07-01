from aiarena.core.utils import TestCase, TransactionTestCase

from aiarena.core.tests.tests import FullDataSetMixin


class ApiReadTestCase(FullDataSetMixin, TransactionTestCase):
    """
    Tests to ensure API endpoint page renders don't break.
    """

    def setUp(self):
        super().setUp()
        self.client.login(username='staff_user', password='x')

    def test_get_api_index_page(self):
        response = self.client.get('/api/')
        self.assertEqual(response.status_code, 200)

    def test_get_api_bots_page(self):
        response = self.client.get('/api/bots/')
        self.assertEqual(response.status_code, 200)

    def test_get_api_maps_page(self):
        response = self.client.get('/api/maps/')
        self.assertEqual(response.status_code, 200)

    def test_get_api_matches_page(self):
        response = self.client.get('/api/matches/')
        self.assertEqual(response.status_code, 200)

    def test_get_api_matchparticipations_page(self):
        response = self.client.get('/api/match-participations/')
        self.assertEqual(response.status_code, 200)

    def test_get_api_seasonparticipations_page(self):
        response = self.client.get('/api/season-participations/')
        self.assertEqual(response.status_code, 200)

    def test_get_api_results_page(self):
        response = self.client.get('/api/results/')
        self.assertEqual(response.status_code, 200)

    def test_get_api_rounds_page(self):
        response = self.client.get('/api/rounds/')
        self.assertEqual(response.status_code, 200)

    def test_get_api_seasons_page(self):
        response = self.client.get('/api/seasons/')
        self.assertEqual(response.status_code, 200)

    def test_get_api_users_page(self):
        response = self.client.get('/api/users/')
        self.assertEqual(response.status_code, 200)
