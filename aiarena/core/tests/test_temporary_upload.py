from django.core.files.base import ContentFile

import pytest

from aiarena.core.models import TemporaryUpload


@pytest.fixture
def match_log(queued_match):
    return queued_match.matchparticipation_set.get(participant_number=1).match_log


def test_copy_fails_when_nothing_was_uploaded(arenaclient_user, match_log):
    upload = TemporaryUpload.create_for_upload(arenaclient_user)

    with pytest.raises(ValueError, match="Upload not found in storage"):
        upload.copy_to_file_field(match_log, "")


def test_delete_from_storage(arenaclient_user):
    upload = TemporaryUpload.create_for_upload(arenaclient_user)
    upload.file.storage.save(upload.file.name, ContentFile(b"log"))
    assert upload.exists_in_storage()

    upload.delete_from_storage()

    assert not upload.exists_in_storage()
