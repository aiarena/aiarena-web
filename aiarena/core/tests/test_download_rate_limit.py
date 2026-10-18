import datetime

from django.contrib.auth.models import AnonymousUser
from django.test import override_settings

import pytest

from aiarena.core.models import DownloadRateLimit
from aiarena.core.models.download_rate_limit import current_hour_window, current_month_window
from aiarena.core.services.download_rate_limiting import check_download_rate_limit, record_download


class _FakeStorage:
    """A non-S3 storage class name, so get_s3_file_size_and_etag uses file.size."""


class _FakeFile:
    def __init__(self, size_bytes):
        self.size = size_bytes
        self.name = "fake"
        self.storage = _FakeStorage()

    def __bool__(self):
        return True


def _kb(n):
    return _FakeFile(n * 1024)


# Small limits keep the arithmetic obvious: 10 KB hourly, 25 KB monthly.
RATE_LIMIT_SETTINGS = dict(DOWNLOAD_RATE_LIMIT_HOURLY_KB=10, DOWNLOAD_RATE_LIMIT_MONTHLY_KB=25)


@pytest.mark.django_db
@override_settings(**RATE_LIMIT_SETTINGS)
def test_grant_increments_bytes_and_granted(user):
    assert record_download(user, _kb(4)) is True

    bucket = DownloadRateLimit.objects.get(user=user)
    assert bucket.hourly_downloads_kb == 4
    assert bucket.monthly_downloads_kb == 4
    assert bucket.granted_downloads == 1
    assert bucket.denied_downloads == 0
    assert bucket.last_hour == current_hour_window()
    assert bucket.last_month == current_month_window()


@pytest.mark.django_db
@override_settings(**RATE_LIMIT_SETTINGS)
def test_rounds_partial_kb_up(user):
    record_download(user, _FakeFile(1025))  # 1 byte over 1 KB -> 2 KB

    assert DownloadRateLimit.objects.get(user=user).hourly_downloads_kb == 2


@pytest.mark.django_db
@override_settings(**RATE_LIMIT_SETTINGS)
def test_hourly_limit_denies_and_freezes_bytes(user):
    assert record_download(user, _kb(8)) is True
    # 8 + 4 = 12 > 10 hourly limit -> deny, bytes frozen.
    assert record_download(user, _kb(4)) is False

    bucket = DownloadRateLimit.objects.get(user=user)
    assert bucket.hourly_downloads_kb == 8
    assert bucket.monthly_downloads_kb == 8
    assert bucket.granted_downloads == 1
    assert bucket.denied_downloads == 1


@pytest.mark.django_db
@override_settings(DOWNLOAD_RATE_LIMIT_HOURLY_KB=1000, DOWNLOAD_RATE_LIMIT_MONTHLY_KB=25)
def test_monthly_limit_denies_independently_of_hourly(user):
    bucket = DownloadRateLimit.objects.create(
        user=user,
        last_hour=current_hour_window(),
        last_month=current_month_window(),
        hourly_downloads_kb=20,
        monthly_downloads_kb=20,
    )
    # 20 + 10 = 30 > 25 monthly limit, even though hourly (1000) has room.
    assert record_download(user, _kb(10)) is False

    bucket.refresh_from_db()
    assert bucket.monthly_downloads_kb == 20
    assert bucket.denied_downloads == 1


@pytest.mark.django_db
@override_settings(**RATE_LIMIT_SETTINGS)
def test_hour_rollover_resets_hourly_only(user):
    DownloadRateLimit.objects.create(
        user=user,
        last_hour="2000-01-01-00",
        last_month=current_month_window(),
        hourly_downloads_kb=9,
        monthly_downloads_kb=9,
        granted_downloads=3,
        denied_downloads=1,
    )

    assert record_download(user, _kb(4)) is True

    bucket = DownloadRateLimit.objects.get(user=user)
    assert bucket.hourly_downloads_kb == 4  # reset then += 4
    assert bucket.monthly_downloads_kb == 13  # 9 + 4, month unchanged
    assert bucket.granted_downloads == 4  # month counters survive the hour rollover
    assert bucket.denied_downloads == 1


@pytest.mark.django_db
@override_settings(**RATE_LIMIT_SETTINGS)
def test_month_rollover_resets_month_counters(user):
    DownloadRateLimit.objects.create(
        user=user,
        last_hour="2000-01-01-00",
        last_month="2000-01",
        hourly_downloads_kb=9,
        monthly_downloads_kb=20,
        granted_downloads=5,
        denied_downloads=2,
    )

    assert record_download(user, _kb(4)) is True

    bucket = DownloadRateLimit.objects.get(user=user)
    assert bucket.hourly_downloads_kb == 4
    assert bucket.monthly_downloads_kb == 4
    assert bucket.granted_downloads == 1  # reset then the single grant
    assert bucket.denied_downloads == 0
    assert bucket.last_hour == current_hour_window()
    assert bucket.last_month == current_month_window()


@pytest.mark.django_db
@override_settings(**RATE_LIMIT_SETTINGS)
def test_anonymous_requests_share_a_single_bucket():
    record_download(AnonymousUser(), _kb(3))
    record_download(None, _kb(2))

    buckets = DownloadRateLimit.objects.filter(is_shared_anonymous=True)
    assert buckets.count() == 1
    assert buckets.get().hourly_downloads_kb == 5
    assert not DownloadRateLimit.objects.filter(is_shared_anonymous=False).exists()


@pytest.mark.django_db
@override_settings(**RATE_LIMIT_SETTINGS)
def test_authenticated_and_anonymous_buckets_are_separate(user):
    record_download(user, _kb(3))
    record_download(AnonymousUser(), _kb(7))

    assert DownloadRateLimit.objects.get(user=user).hourly_downloads_kb == 3
    assert DownloadRateLimit.objects.get(is_shared_anonymous=True).hourly_downloads_kb == 7


@pytest.mark.django_db
def test_check_download_rate_limit_ignores_missing_file(user):
    assert check_download_rate_limit(user, None) is True
    assert not DownloadRateLimit.objects.exists()


@pytest.mark.django_db
def test_check_download_rate_limit_swallows_errors(user, monkeypatch):
    def boom(*args, **kwargs):
        raise RuntimeError("S3 unavailable")

    monkeypatch.setattr("aiarena.core.services.download_rate_limiting.record_download", boom)
    # Must not raise and must fail open -- a failure in accounting can never break a download.
    assert check_download_rate_limit(user, _kb(1)) is True


def test_window_strings_are_utc():
    aware = datetime.datetime(2026, 10, 18, 23, 30, tzinfo=datetime.UTC)
    assert current_hour_window(aware) == "2026-10-18-23"
    assert current_month_window(aware) == "2026-10"
