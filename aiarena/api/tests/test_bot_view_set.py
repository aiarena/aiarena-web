from django.test import TestCase
from django.urls import reverse

from rest_framework.test import APIClient

from aiarena.core.tests.test_mixins import MatchReadyMixin


class BotSerializerTestCase(MatchReadyMixin, TestCase):
    def test_download_bot_zip_success(self):
        """
        Note that this test is for essentially a defunct feature. Downloads would be via AWS S3.
        """
        self.client = APIClient()
        self.client.force_authenticate(user=self.regularUser1)
        bot = self.regularUser1Bot1  # owned by the current user

        # URL base name for BotViewSet is api_bot, action url_path is zip
        self.url = reverse("api_bot-download-zip", kwargs={"pk": bot.id})
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)

    def test_download_bot_zip_unauthorized(self):
        """
        Note that this test is for essentially a defunct feature. Downloads would be via AWS S3.
        """
        self.client = APIClient()
        self.client.force_authenticate(user=self.regularUser1)
        bot = self.staffUser1Bot1  # owned by someone else

        # URL base name for BotViewSet is api_bot, action url_path is zip
        self.url = reverse("api_bot-download-zip", kwargs={"pk": bot.id})
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 404)
