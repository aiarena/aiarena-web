import logging
import math

from django.conf import settings
from django.db import transaction

from aiarena.core.models import DownloadRateLimit
from aiarena.core.models.download_rate_limit import current_hour_window, current_month_window
from aiarena.core.s3_helpers import get_s3_file_size_and_etag


logger = logging.getLogger(__name__)


def record_download(user, file) -> bool:
    """Meter a download of `file` by `user`; return whether it is within limits.

    A would-grant adds the file's size to the hourly and monthly counters; a
    would-deny bumps only the denied count (byte counters stay frozen).
    """
    size_bytes, _etag = get_s3_file_size_and_etag(file)
    size_kb = math.ceil(size_bytes / 1024)

    is_anonymous = user is None or not getattr(user, "is_authenticated", False)

    with transaction.atomic():
        if is_anonymous:
            bucket, _ = DownloadRateLimit.objects.select_for_update().get_or_create(is_shared_anonymous=True)
        else:
            bucket, _ = DownloadRateLimit.objects.select_for_update().get_or_create(user=user)

        hour = current_hour_window()
        month = current_month_window()

        if bucket.last_hour != hour:
            bucket.last_hour = hour
            bucket.hourly_downloads_kb = 0
        if bucket.last_month != month:
            bucket.last_month = month
            bucket.monthly_downloads_kb = 0
            bucket.granted_downloads = 0
            bucket.denied_downloads = 0

        would_grant = (
            bucket.hourly_downloads_kb + size_kb <= settings.DOWNLOAD_RATE_LIMIT_HOURLY_KB
            and bucket.monthly_downloads_kb + size_kb <= settings.DOWNLOAD_RATE_LIMIT_MONTHLY_KB
        )

        if would_grant:
            bucket.hourly_downloads_kb += size_kb
            bucket.monthly_downloads_kb += size_kb
            bucket.granted_downloads += 1
        else:
            bucket.denied_downloads += 1

        bucket.save()

    return would_grant


def check_download_rate_limit(user, file) -> bool:
    """Single entry point for every download link/serve site: meter the download and
    return whether it is within limits.

    Fails open -- if the accounting errors, the download is allowed and the error is
    logged. In the current observe-mode rollout callers ignore the return value.
    """
    if not file:
        return True
    try:
        return record_download(user, file)
    except Exception:
        logger.exception("Download rate-limit accounting failed")
        return True

