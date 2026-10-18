import datetime

from django.conf import settings
from django.db import models


HOUR_WINDOW_FORMAT = "%Y-%m-%d-%H"
MONTH_WINDOW_FORMAT = "%Y-%m"


def current_hour_window(now: datetime.datetime | None = None) -> str:
    """UTC hour window string, e.g. "2026-10-18-23"."""
    now = now or datetime.datetime.now(tz=datetime.UTC)
    return now.astimezone(datetime.UTC).strftime(HOUR_WINDOW_FORMAT)


def current_month_window(now: datetime.datetime | None = None) -> str:
    """UTC month window string, e.g. "2026-10"."""
    now = now or datetime.datetime.now(tz=datetime.UTC)
    return now.astimezone(datetime.UTC).strftime(MONTH_WINDOW_FORMAT)


class DownloadRateLimit(models.Model):
    """Per-user download accounting for rate limiting.

    One row per user; a single row with user=NULL is the shared anonymous bucket.
    Window columns are UTC strings compared by exact match ("YYYY-MM-DD-HH",
    "YYYY-MM"); volumes are kilobytes rounded up per file, which keeps them within a
    4-byte integer even at the largest monthly tier.
    """

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.CASCADE,
        related_name="download_rate_limit",
    )
    # Vehicle for the partial unique index that enforces a single anonymous bucket
    # row. Postgres treats multiple NULLs in a unique index as distinct, so a unique
    # index on `user` alone would not stop duplicate anonymous rows. Django 5's
    # UniqueConstraint(nulls_distinct=False) would let us drop this column and key
    # the index directly on a NULL `user` -- worth revisiting when the team discusses
    # upgrading to Django 5.
    is_shared_anonymous = models.BooleanField(default=False)

    last_hour = models.CharField(max_length=13, blank=True)
    last_month = models.CharField(max_length=7, blank=True)

    hourly_downloads_kb = models.IntegerField(default=0)
    monthly_downloads_kb = models.IntegerField(default=0)

    # Cumulative counts within the current monthly window (reset on month rollover).
    granted_downloads = models.IntegerField(default=0)
    denied_downloads = models.IntegerField(default=0)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["is_shared_anonymous"],
                condition=models.Q(is_shared_anonymous=True),
                name="single_anonymous_download_bucket",
            )
        ]

    def __str__(self):
        who = "anonymous" if self.user_id is None else self.user.username
        return f"DownloadRateLimit({who})"
