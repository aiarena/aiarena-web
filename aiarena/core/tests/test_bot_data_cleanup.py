from io import StringIO

from django.core.files.base import ContentFile
from django.core.management import call_command
from django.db import transaction

import pytest

from aiarena.core.models import Bot


@pytest.fixture
def storage():
    return Bot._meta.get_field("bot_data").storage


@pytest.fixture
def bot_with_data(bot):
    bot.bot_data = ContentFile(b"old data", name="data.zip")
    bot.save()
    return bot


def test_replacing_bot_data_deletes_old_file_after_commit(bot_with_data, storage, django_capture_on_commit_callbacks):
    old_name = bot_with_data.bot_data.name

    with django_capture_on_commit_callbacks(execute=False) as callbacks:
        bot_with_data.bot_data = ContentFile(b"new data", name="data.zip")
        bot_with_data.save()
    assert storage.exists(old_name)  # not deleted before commit

    for callback in callbacks:
        callback()
    assert not storage.exists(old_name)
    assert storage.exists(bot_with_data.bot_data.name)


def test_clearing_bot_data_deletes_old_file(bot_with_data, storage, django_capture_on_commit_callbacks):
    old_name = bot_with_data.bot_data.name

    with django_capture_on_commit_callbacks(execute=True):
        bot_with_data.bot_data = None
        bot_with_data.save()

    assert not storage.exists(old_name)


def test_saving_without_changing_bot_data_keeps_file(bot_with_data, storage, django_capture_on_commit_callbacks):
    with django_capture_on_commit_callbacks(execute=True):
        bot_with_data.bot_data_publicly_downloadable = True
        bot_with_data.save()

    assert storage.exists(bot_with_data.bot_data.name)


def test_rolled_back_replacement_keeps_old_file(bot_with_data, storage, django_capture_on_commit_callbacks):
    old_name = bot_with_data.bot_data.name

    with django_capture_on_commit_callbacks(execute=True) as callbacks:
        with pytest.raises(RuntimeError), transaction.atomic():
            bot_with_data.bot_data = ContentFile(b"new data", name="data.zip")
            bot_with_data.save()
            raise RuntimeError

    assert callbacks == []
    assert storage.exists(old_name)


def test_cleanup_orphaned_bot_data_command(bot_with_data, storage):
    orphan_name = storage.save(f"bots/{bot_with_data.id}/bot_data_1", ContentFile(b"orphan"))
    bot_zip_name = bot_with_data.bot_zip.name

    out = StringIO()
    call_command("cleanuporphanedbotdata", "--min-age-minutes=0", stdout=out)
    assert "Found 1 orphaned bot_data files." in out.getvalue()
    assert storage.exists(orphan_name)

    call_command("cleanuporphanedbotdata", "--min-age-minutes=0", "--delete", stdout=out)
    assert not storage.exists(orphan_name)
    assert storage.exists(bot_with_data.bot_data.name)
    assert storage.exists(bot_zip_name)
