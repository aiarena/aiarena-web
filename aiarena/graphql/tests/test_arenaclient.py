from unittest import mock

from aiarena.core.models import ArenaClient, TemporaryUpload
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
        fake_url = "https://example.invalid/temp-uploads/abc?signed=1"
        with mock.patch.object(TemporaryUpload, "generate_presigned_put_url", return_value=fake_url):
            response = self.mutate(
                login_user=arenaclient_user,
                variables={"input": {"count": 3}},
            )

        uploads = response["requestUploadUrls"]["uploads"]
        assert len(uploads) == 3
        assert all(u["uploadUrl"] == fake_url for u in uploads)
        assert TemporaryUpload.objects.filter(uploaded_by=arenaclient_user).count() == 3

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
    """GraphQL-level coverage of SubmitResult's access guards. The full
    result-processing happy path is exercised by the arena-client integration
    tests; here we pin the security boundaries: who may submit, for which match,
    and with whose uploads."""

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
