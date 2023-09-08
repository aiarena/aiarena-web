from django.test import TransactionTestCase

from aiarena.core.tests.test_mixins import FullDataSetMixin


class SessionBasedAuthTestCase(FullDataSetMixin, TransactionTestCase):
    def test_session_based_auth(self):
        self.client.logout()  # ensure we're not already logged in

        # Should be no current user
        response = self.client.get("/api/auth/")
        self.assertEqual(response.status_code, 200)
        self.assertIsNone(response.data["current_user"])

        # Login
        response = self.client.post("/api/auth/login/", {"username": "staff_user", "password": "x"})
        self.assertEqual(response.status_code, 202)

        # Current user should be staff_user
        response = self.client.get("/api/auth/")
        self.assertEqual(response.data["current_user"]["username"], "staff_user")

        # Logout
        response = self.client.post("/api/auth/logout/")
        self.assertEqual(response.status_code, 204)

        # Should be no current user
        response = self.client.get("/api/auth/")
        self.assertEqual(response.status_code, 200)
        self.assertIsNone(response.data["current_user"])
