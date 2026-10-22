from django.core.files.base import ContentFile

import requests

from aiarena.core.models import ArenaClient, Bot, TemporaryUpload
from aiarena.core.tests.base import GraphQLTest
from aiarena.graphql import MatchType, TemporaryUploadType
from aiarena.graphql.common import NOT_LOGGED_IN_MESSAGE


class TestRequestUploadUrls(GraphQLTest):
    mutation_name = "requestUploadUrls"
    # language=graphql
    mutation = """
        mutation ($input: RequestUploadUrlsInput!) {
            requestUploadUrls(input: $input) {
                uploads {
                    upload { id }
                    uploadUrl
                }
                errors { messages field }
            }
        }
    """

    def test_happy_path(self, arenaclient_user):
        response = self.mutate(
            login_user=arenaclient_user,
            variables={"input": {"count": 3}},
        )

        upload_urls = [u["uploadUrl"] for u in response["requestUploadUrls"]["uploads"]]
        uploads = TemporaryUpload.objects.filter(uploaded_by=arenaclient_user)
        assert len(upload_urls) == uploads.count() == 3

        # Each URL is a working presigned PUT for its own upload record's key.
        for upload in uploads:
            [url] = [url for url in upload_urls if upload.file.name in url]
            assert not upload.exists_in_storage()
            requests.put(url, data=b"uploaded by the arena client").raise_for_status()
            assert upload.exists_in_storage()

    def test_count_too_high(self, arenaclient_user):
        self.mutate(
            login_user=arenaclient_user,
            variables={"input": {"count": 11}},
            expected_validation_errors={"count": ["Count must be between 1 and 10."]},
        )
        assert TemporaryUpload.objects.count() == 0

    def test_count_too_low(self, arenaclient_user):
        self.mutate(
            login_user=arenaclient_user,
            variables={"input": {"count": 0}},
            expected_validation_errors={"count": ["Count must be between 1 and 10."]},
        )

    def test_not_authenticated(self, db):
        self.mutate(
            variables={"input": {"count": 1}},
            expected_errors_like=[NOT_LOGGED_IN_MESSAGE],
        )

    def test_not_arenaclient(self, user):
        self.mutate(
            login_user=user,
            variables={"input": {"count": 1}},
            expected_errors_like=["Only arena clients can request upload URLs."],
        )


class TestGetNextMatch(GraphQLTest):
    mutation_name = "getNextMatch"
    # language=graphql
    mutation = """
        mutation {
            getNextMatch {
                match { id }
            }
        }
    """

    def test_not_authenticated(self, db):
        self.mutate(expected_errors_like=[NOT_LOGGED_IN_MESSAGE])

    def test_not_arenaclient(self, user):
        self.mutate(
            login_user=user,
            expected_errors_like=["Only arena clients can get matches."],
        )


class TestSubmitResult(GraphQLTest):
    """SubmitResult end to end against fake S3 (files are uploaded to presigned URLs, then copied into place), plus
    the security boundaries: who may submit, for which match, and with whose uploads."""

    mutation_name = "submitResult"
    # language=graphql
    mutation = """
        mutation ($input: SubmitResultInput!) {
            submitResult(input: $input) {
                errors { messages field }
            }
        }
    """

    def _assigned_match(self, arenaclient_user, queued_match):
        queued_match.assigned_to = arenaclient_user
        queued_match.save()
        return queued_match

    @staticmethod
    def _upload(arenaclient_user, content: bytes) -> TemporaryUpload:
        """Upload a file the way an arena client does: to a presigned URL."""
        upload = TemporaryUpload.create_for_upload(arenaclient_user)
        requests.put(upload.generate_presigned_put_url(), data=content).raise_for_status()
        return upload

    def _submit_with_all_files(self, arenaclient_user, match) -> dict[str, TemporaryUpload]:
        uploads = {
            field: self._upload(arenaclient_user, f"{field} content".encode())
            for field in ["replayFile", "arenaclientLog", "bot1Data", "bot2Data", "bot1Log", "bot2Log"]
        }
        self.mutate(
            login_user=arenaclient_user,
            variables={
                "input": {
                    "match": self.to_global_id(MatchType, match.id),
                    "type": "Player1Win",
                    "gameSteps": 1000,
                    **{field: self.to_global_id(TemporaryUploadType, upload.id) for field, upload in uploads.items()},
                }
            },
        )
        return uploads

    @staticmethod
    def _give_bot_data(bot: Bot, content: bytes) -> str:
        bot.bot_data = ContentFile(content, name="data.zip")
        bot.save()
        return bot.bot_data.name

    def test_submit_result_with_files(
        self, arenaclient_user, queued_match, bot, other_bot, django_capture_on_commit_callbacks
    ):
        match = self._assigned_match(arenaclient_user, queued_match)
        old_bot1_data = self._give_bot_data(bot, b"old bot1 data")
        old_bot2_data = self._give_bot_data(other_bot, b"old bot2 data")
        private_storage = Bot._meta.get_field("bot_data").storage

        with django_capture_on_commit_callbacks(execute=True):
            uploads = self._submit_with_all_files(arenaclient_user, match)

        match.refresh_from_db()
        result = match.result
        assert result.type == "Player1Win"
        assert result.replay_file.read() == b"replayFile content"
        assert result.arenaclient_log.read() == b"arenaclientLog content"

        p1 = match.matchparticipation_set.get(participant_number=1)
        p2 = match.matchparticipation_set.get(participant_number=2)
        assert p1.match_log.read() == b"bot1Log content"
        assert p2.match_log.read() == b"bot2Log content"

        # New bot data is in place, and the files it replaced are gone.
        bot.refresh_from_db()
        other_bot.refresh_from_db()
        assert bot.bot_data.read() == b"bot1Data content"
        assert other_bot.bot_data.read() == b"bot2Data content"
        assert not private_storage.exists(old_bot1_data)
        assert not private_storage.exists(old_bot2_data)

        # The temporary uploads are cleaned up, both the records and the files.
        assert not TemporaryUpload.objects.exists()
        assert not any(upload.exists_in_storage() for upload in uploads.values())

    def test_requested_match_does_not_update_bot_data(
        self, arenaclient_user, queued_match, bot, user, django_capture_on_commit_callbacks
    ):
        match = self._assigned_match(arenaclient_user, queued_match)
        match.requested_by = user
        match.save()
        old_bot1_data = self._give_bot_data(bot, b"old bot1 data")

        with django_capture_on_commit_callbacks(execute=True):
            self._submit_with_all_files(arenaclient_user, match)

        bot.refresh_from_db()
        assert bot.bot_data.name == old_bot1_data
        assert bot.bot_data.read() == b"old bot1 data"
        assert not TemporaryUpload.objects.exists()

    def test_not_authenticated(self, db):
        self.mutate(
            variables={"input": {"type": "Player1Win", "gameSteps": 1}},
            expected_errors_like=[NOT_LOGGED_IN_MESSAGE],
        )

    def test_non_arenaclient_cannot_submit(self, user, queued_match):
        """A non-arena-client is denied. The match-assignment check (clean_match)
        fires first — a regular user can never be a match's assigned_to — so they
        never reach the is_arenaclient guard in the body. Either way: denied, no
        result written."""
        self.mutate(
            login_user=user,
            variables={
                "input": {
                    "match": self.to_global_id(MatchType, queued_match.id),
                    "type": "Player1Win",
                    "gameSteps": 1,
                }
            },
            expected_validation_errors={"match": ["Match is not assigned to this arena client."]},
        )
        queued_match.refresh_from_db()
        assert queued_match.result is None

    def test_cannot_submit_for_match_not_assigned_to_you(self, arenaclient_user, queued_match):
        """The match isn't assigned to this client — clean_match rejects it."""
        assert queued_match.assigned_to is None

        self.mutate(
            login_user=arenaclient_user,
            variables={
                "input": {
                    "match": self.to_global_id(MatchType, queued_match.id),
                    "type": "Player1Win",
                    "gameSteps": 1,
                }
            },
            expected_validation_errors={"match": ["Match is not assigned to this arena client."]},
        )
        queued_match.refresh_from_db()
        assert queued_match.result is None

    def test_cannot_reference_another_clients_upload(self, arenaclient_user, admin_user, queued_match):
        """IDOR guard: a client can't reference a TemporaryUpload it didn't create,
        even on a match correctly assigned to it."""
        match = self._assigned_match(arenaclient_user, queued_match)

        other_client = ArenaClient.objects.create(
            username="ac2",
            email="ac2@dev.aiarena.net",
            type="ARENA_CLIENT",
            trusted=True,
            owner=admin_user,
        )
        other_clients_upload = TemporaryUpload.create_for_upload(other_client)

        self.mutate(
            login_user=arenaclient_user,
            variables={
                "input": {
                    "match": self.to_global_id(MatchType, match.id),
                    "type": "Player1Win",
                    "gameSteps": 1,
                    "bot1Log": self.to_global_id(TemporaryUploadType, other_clients_upload.id),
                }
            },
            expected_validation_errors={"bot1Log": ["Upload was not created by this arena client."]},
        )
        match.refresh_from_db()
        assert match.result is None
