import logging
import math

from django.conf import settings
from django.db.models import F, Sum

from aiarena.core.models import DownloadDenial, DownloadRecord
from aiarena.core.models.download_rate_limit import (
    current_hour_window,
    hour_window_start,
    month_window_start,
)
from aiarena.core.s3_helpers import get_s3_file_size_and_etag


logger = logging.getLogger(__name__)


def record_download(user, file) -> bool:
    """Meter a download of `file` by `user`; return whether it is within limits.

    A within-limits download is recorded as a DownloadRecord row -- it moves bytes
    and counts toward the budget. An over-limit download is tallied on the user's
    DownloadDenial counter instead of rowed, so rejection floods can't bloat the
    table. In observe mode the caller issues the link regardless of the return.
    """
    size_bytes, _etag = get_s3_file_size_and_etag(file)
    size_kb = math.ceil(size_bytes / 1024)

    # One shared bucket (NULL user) for all anonymous traffic.
    user = user if user is not None and getattr(user, "is_authenticated", False) else None

    # Append-only read + insert, no lock: the limit is a cost safeguard, so a rare
    # concurrent overshoot of a few KB is acceptable and not worth serializing for.
    consumed = DownloadRecord.objects.filter(user=user)
    hourly_kb = consumed.filter(created_at__gte=hour_window_start()).aggregate(s=Sum("size_kb"))["s"] or 0
    monthly_kb = consumed.filter(created_at__gte=month_window_start()).aggregate(s=Sum("size_kb"))["s"] or 0

    within_limits = (
        hourly_kb + size_kb <= settings.DOWNLOAD_RATE_LIMIT_HOURLY_KB
        and monthly_kb + size_kb <= settings.DOWNLOAD_RATE_LIMIT_MONTHLY_KB
    )

    if within_limits:
        DownloadRecord.objects.create(user=user, size_kb=size_kb)
    else:
        _tally_denial(user, size_kb)

    return within_limits


def _tally_denial(user, size_kb: int) -> None:
    """Increment the (user, current-hour) denial counter without holding a lock
    across the request.

    The increment is a single atomic UPDATE (no select_for_update, no Python
    read-modify-write), and it gates nothing -- so even under a flood it only slows
    the counter writes, never a download. See aiarena/core/services/CLAUDE.md for
    why a single hot counter row is acceptable and the sharding escape hatch.
    """
    window = current_hour_window()
    counter, _ = DownloadDenial.objects.get_or_create(user=user, window=window)
    DownloadDenial.objects.filter(pk=counter.pk).update(
        count=F("count") + 1,
        size_kb=F("size_kb") + size_kb,
    )


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
