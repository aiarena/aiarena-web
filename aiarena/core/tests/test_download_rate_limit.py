import datetime

from django.contrib.auth.models import AnonymousUser
from django.test import override_settings

import pytest

from aiarena.core.models import DownloadDenial, DownloadRecord
from aiarena.core.models.download_rate_limit import current_hour_window, hour_window_start, month_window_start
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


def _backdate(queryset, when):
    """Override auto_now_add created_at so window boundaries can be exercised."""
    queryset.update(created_at=when)


# Small limits keep the arithmetic obvious: 10 KB hourly, 25 KB monthly.
RATE_LIMIT_SETTINGS = dict(DOWNLOAD_RATE_LIMIT_HOURLY_KB=10, DOWNLOAD_RATE_LIMIT_MONTHLY_KB=25)


@pytest.mark.django_db
@override_settings(**RATE_LIMIT_SETTINGS)
def test_within_limits_creates_a_record(user):
    assert record_download(user, _kb(4)) is True

    records = DownloadRecord.objects.filter(user=user)
    assert records.count() == 1
    assert records.get().size_kb == 4
    assert not DownloadDenial.objects.exists()


@pytest.mark.django_db
@override_settings(**RATE_LIMIT_SETTINGS)
def test_rounds_partial_kb_up(user):
    record_download(user, _FakeFile(1025))  # 1 byte over 1 KB -> 2 KB

    assert DownloadRecord.objects.get(user=user).size_kb == 2


@pytest.mark.django_db
@override_settings(**RATE_LIMIT_SETTINGS)
def test_hourly_limit_denies_and_does_not_record(user):
    assert record_download(user, _kb(8)) is True
    # 8 + 4 = 12 > 10 hourly limit -> deny: no record, denial counter instead.
    assert record_download(user, _kb(4)) is False

    assert DownloadRecord.objects.filter(user=user).count() == 1  # only the grant
    denial = DownloadDenial.objects.get(user=user, window=current_hour_window())
    assert denial.count == 1
    assert denial.size_kb == 4  # the would-be bytes are tallied


@pytest.mark.django_db
@override_settings(DOWNLOAD_RATE_LIMIT_HOURLY_KB=1000, DOWNLOAD_RATE_LIMIT_MONTHLY_KB=25)
def test_monthly_limit_denies_independently_of_hourly(user):
    # 20 KB already consumed this month, spread so the hourly window has room.
    record_download(user, _kb(20))
    _backdate(DownloadRecord.objects.filter(user=user), month_window_start() + datetime.timedelta(minutes=1))

    # 20 + 10 = 30 > 25 monthly limit, even though hourly (1000) has room.
    assert record_download(user, _kb(10)) is False

    assert DownloadRecord.objects.filter(user=user).count() == 1  # the denial was not recorded
    assert DownloadDenial.objects.get(user=user).size_kb == 10


@pytest.mark.django_db
@override_settings(**RATE_LIMIT_SETTINGS)
def test_records_outside_the_hour_do_not_count_toward_hourly(user):
    record_download(user, _kb(9))
    # Push that grant into a previous hour (but the same month).
    old = hour_window_start() - datetime.timedelta(hours=2)
    _backdate(DownloadRecord.objects.filter(user=user), old)

    # Hourly window is now empty, so 4 KB is granted despite the stale 9 KB.
    assert record_download(user, _kb(4)) is True
    assert DownloadRecord.objects.filter(user=user).count() == 2


@pytest.mark.django_db
@override_settings(**RATE_LIMIT_SETTINGS)
def test_records_outside_the_month_do_not_count_toward_monthly(user):
    record_download(user, _kb(8))
    # Push that grant into a previous month.
    old = month_window_start() - datetime.timedelta(days=1)
    _backdate(DownloadRecord.objects.filter(user=user), old)

    # Both windows are now empty, so a fresh 8 KB is granted.
    assert record_download(user, _kb(8)) is True
    assert DownloadRecord.objects.filter(user=user, created_at__gte=month_window_start()).count() == 1


@pytest.mark.django_db
@override_settings(**RATE_LIMIT_SETTINGS)
def test_anonymous_requests_share_a_single_bucket():
    assert record_download(AnonymousUser(), _kb(3)) is True
    assert record_download(None, _kb(2)) is True

    anon = DownloadRecord.objects.filter(user__isnull=True)
    assert anon.count() == 2
    # Both counted against the one NULL-user bucket: 3 + 2 = 5, under the 10 limit.
    assert record_download(AnonymousUser(), _kb(5)) is True
    assert record_download(AnonymousUser(), _kb(1)) is False  # 5 + 1 ... 3+2+5=10, +1 over


@pytest.mark.django_db
@override_settings(**RATE_LIMIT_SETTINGS)
def test_authenticated_and_anonymous_buckets_are_separate(user):
    record_download(user, _kb(3))
    record_download(AnonymousUser(), _kb(7))

    assert DownloadRecord.objects.get(user=user).size_kb == 3
    assert DownloadRecord.objects.get(user__isnull=True).size_kb == 7


@pytest.mark.django_db
@override_settings(**RATE_LIMIT_SETTINGS)
def test_repeated_denials_collapse_into_one_counter_row(user):
    record_download(user, _kb(10))  # fill the hourly limit
    for _ in range(5):
        assert record_download(user, _kb(4)) is False

    denial = DownloadDenial.objects.get(user=user, window=current_hour_window())
    assert denial.count == 5
    assert denial.size_kb == 20  # 5 * 4 KB of would-be bytes


@pytest.mark.django_db
def test_check_download_rate_limit_ignores_missing_file(user):
    assert check_download_rate_limit(user, None) is True
    assert not DownloadRecord.objects.exists()


@pytest.mark.django_db
def test_check_download_rate_limit_swallows_errors(user, monkeypatch):
    def boom(*args, **kwargs):
        raise RuntimeError("S3 unavailable")

    monkeypatch.setattr("aiarena.core.services.download_rate_limiting.record_download", boom)
    # Must not raise and must fail open -- a failure in accounting can never break a download.
    assert check_download_rate_limit(user, _kb(1)) is True


def test_window_helpers_are_utc():
    aware = datetime.datetime(2026, 10, 18, 23, 30, tzinfo=datetime.UTC)
    assert current_hour_window(aware) == "2026-10-18-23"
    assert hour_window_start(aware) == datetime.datetime(2026, 10, 18, 23, 0, tzinfo=datetime.UTC)
    assert month_window_start(aware) == datetime.datetime(2026, 10, 1, 0, 0, tzinfo=datetime.UTC)


def test_retention_cutoff_keeps_the_last_n_calendar_months():
    from aiarena.core.management.commands.prunedownloadrecords import retention_cutoff

    now = datetime.datetime(2026, 10, 24, 12, 0, tzinfo=datetime.UTC)
    # 3 months retained -> keep Aug, Sep, Oct; cut off at Aug 1.
    assert retention_cutoff(now, 3) == datetime.datetime(2026, 8, 1, tzinfo=datetime.UTC)


def test_retention_cutoff_wraps_across_the_year():
    from aiarena.core.management.commands.prunedownloadrecords import retention_cutoff

    now = datetime.datetime(2026, 1, 15, tzinfo=datetime.UTC)
    # 3 months retained from January -> keep Nov, Dec, Jan; cut off at Nov 1 of the prior year.
    assert retention_cutoff(now, 3) == datetime.datetime(2025, 11, 1, tzinfo=datetime.UTC)
