from pathlib import Path
from unittest.mock import patch

from django.test import TransactionTestCase
from django.test.client import MULTIPART_CONTENT
from django.urls import reverse

from constance.test import override_config

from aiarena.core.tests.test_mixins import FullDataSetMixin
from aiarena.core.utils import calculate_md5


class ApiBotUploadTestCase(FullDataSetMixin, TransactionTestCase):
    def setUp(self):
        super().setUp()
        self.client.login(username="regular_user1", password="x")
        self.url = reverse("api_bot-detail", kwargs={"pk": self.regularUser1Bot1.pk})
        self.data_dir = Path(__file__).parent / "test_data"
        self.hashes = {
            "minimal_valid_bot.zip": calculate_md5(self.data_dir / "minimal_valid_bot.zip"),
            "invalid_bot.zip": calculate_md5(self.data_dir / "invalid_bot.zip"),
            "too_large_bot.zip": calculate_md5(self.data_dir / "too_large_bot.zip"),
            "bot_data.zip": calculate_md5(self.data_dir / "bot_data.zip"),
        }

    def update_bot(self, path, data, expected_code=200):
        response = self.client.patch(
            path=path,
            data=self.client._encode_data(data, MULTIPART_CONTENT),
            content_type=MULTIPART_CONTENT,
        )
        self.assertEqual(response.status_code, expected_code)
        return response

    def assertApiError(self, response, error_text):
        response_text = response.content.decode()
        self.assertIn(error_text, response_text)

    def test_update_fields(self):
        self.assertEqual(self.regularUser1Bot1.bot_zip_publicly_downloadable, False)
        self.assertEqual(self.regularUser1Bot1.bot_data_publicly_downloadable, False)
        self.assertEqual(self.regularUser1Bot1.bot_data_enabled, True)
        self.assertEqual(self.regularUser1Bot1.wiki_article.current_revision.content, "")
        self.assertNotEqual(self.regularUser1Bot1.bot_zip_md5hash, self.hashes["minimal_valid_bot.zip"])
        self.assertNotEqual(self.regularUser1Bot1.bot_data_md5hash, self.hashes["bot_data.zip"])

        with (
            open(self.data_dir / "minimal_valid_bot.zip", "rb") as bot_zip,
            open(self.data_dir / "bot_data.zip", "rb") as bot_data,
        ):
            self.update_bot(
                path=self.url,
                data={
                    "bot_zip": bot_zip,
                    "bot_data": bot_data,
                    "bot_zip_publicly_downloadable": True,
                    "bot_data_publicly_downloadable": True,
                    "bot_data_enabled": False,
                    "wiki_article_content": "foo",
                },
            )

        self.regularUser1Bot1.refresh_from_db()
        self.assertEqual(self.regularUser1Bot1.bot_zip_publicly_downloadable, True)
        self.assertEqual(self.regularUser1Bot1.bot_data_publicly_downloadable, True)
        self.assertEqual(self.regularUser1Bot1.bot_data_enabled, False)
        self.assertEqual(self.regularUser1Bot1.wiki_article.current_revision.content, "foo")
        self.assertEqual(self.regularUser1Bot1.bot_zip_md5hash, self.hashes["minimal_valid_bot.zip"])
        self.assertEqual(self.regularUser1Bot1.bot_data_md5hash, self.hashes["bot_data.zip"])

    def test_bot_zip_structure_checked(self):
        with open(self.data_dir / "invalid_bot.zip", "rb") as bot_zip:
            response = self.update_bot(
                path=self.url,
                data={"bot_zip": bot_zip},
                expected_code=400,
            )
        self.assertApiError(
            response,
            "Incorrect bot zip file structure.",
        )

    @override_config(BOT_ZIP_SIZE_LIMIT_IN_MB_FREE_TIER=1)
    def test_bot_zip_size_checked(self):
        with open(self.data_dir / "too_large_bot.zip", "rb") as bot_zip:
            response = self.update_bot(
                path=self.url,
                data={"bot_zip": bot_zip},
                expected_code=400,
            )
        self.assertApiError(
            response,
            "File too large. Size should not exceed 1 MB.",
        )

    def test_cannot_update_non_editable_field(self):
        self.assertNotEqual(self.regularUser1Bot1.name, "newName")

        # It will accept the unknown fields, but swallow them
        self.update_bot(
            path=self.url,
            data={"name": "newName"},
            expected_code=200,
        )

        self.regularUser1Bot1.refresh_from_db()
        self.assertNotEqual(self.regularUser1Bot1.name, "newName")

    def test_anonymous_user_cannot_update(self):
        self.client.logout()
        self.assertEqual(self.regularUser1Bot1.bot_zip_publicly_downloadable, False)

        response = self.update_bot(
            path=self.url,
            data={"bot_zip_publicly_downloadable": True},
            expected_code=403,
        )
        self.assertApiError(response, "Authentication credentials were not provided")

        self.regularUser1Bot1.refresh_from_db()
        self.assertEqual(self.regularUser1Bot1.bot_zip_publicly_downloadable, False)

    def test_non_owner_cannot_update(self):
        self.client.login(username="regular_user2", password="x")
        self.assertEqual(self.regularUser1Bot1.bot_zip_publicly_downloadable, False)

        response = self.update_bot(
            path=self.url,
            data={"bot_zip_publicly_downloadable": True},
            expected_code=403,
        )
        self.assertApiError(response, "You cannot edit a bot that belongs to someone else")

        self.regularUser1Bot1.refresh_from_db()
        self.assertEqual(self.regularUser1Bot1.bot_zip_publicly_downloadable, False)

    @patch("aiarena.core.services.service_implementations.Bots.bot_data_is_frozen", lambda self, bot: True)
    def test_data_not_updated_while_frozen(self):
        self.assertEqual(self.regularUser1Bot1.bot_zip_publicly_downloadable, False)
        self.assertNotEqual(self.regularUser1Bot1.bot_data_md5hash, self.hashes["bot_data.zip"])

        self.update_bot(
            path=self.url,
            data={"bot_zip_publicly_downloadable": True},
            expected_code=200,
        )
        with open(self.data_dir / "bot_data.zip", "rb") as bot_data:
            response = self.update_bot(
                path=self.url,
                data={"bot_data": bot_data},
                expected_code=400,
            )

        self.assertApiError(
            response,
            "Cannot edit bot_data when it's frozen",
        )

        # bot_zip_publicly_downloadable got updated, but bot_data didn't get updated
        self.regularUser1Bot1.refresh_from_db()
        self.assertEqual(self.regularUser1Bot1.bot_zip_publicly_downloadable, True)
        self.assertNotEqual(self.regularUser1Bot1.bot_data_md5hash, self.hashes["bot_data.zip"])
