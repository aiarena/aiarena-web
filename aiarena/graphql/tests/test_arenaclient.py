from unittest import mock

import pytest

from aiarena.core.models import ArenaClient, TemporaryUpload
from aiarena.core.tests.base import GraphQLTest


@pytest.fixture
def arenaclient_user(db, admin_user):
    return ArenaClient.objects.create(
        username="ac1",
        email="ac1@dev.aiarena.net",
        type="ARENA_CLIENT",
        trusted=True,
        owner=admin_user,
    )


class TestRequestUploadUrls(GraphQLTest):
    mutation_name = "requestUploadUrls"
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
            expected_errors_like=["Authentication required."],
        )

    def test_not_arenaclient(self, user):
        self.mutate(
            login_user=user,
            variables={"input": {"count": 1}},
            expected_errors_like=["Only arena clients can request upload URLs."],
        )
