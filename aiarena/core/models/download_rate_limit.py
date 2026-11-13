import datetime

from django.conf import settings
from django.db import models


HOUR_WINDOW_FORMAT = "%Y-%m-%d-%H"


def current_hour_window(now: datetime.datetime | None = None) -> str:
    """UTC hour-window string, e.g. "2026-10-18-23" -- the denial counter's bucket."""
    now = now or datetime.datetime.now(tz=datetime.UTC)
    return now.astimezone(datetime.UTC).strftime(HOUR_WINDOW_FORMAT)


def hour_window_start(now: datetime.datetime | None = None) -> datetime.datetime:
    """Start of the current calendar UTC hour."""
    now = (now or datetime.datetime.now(tz=datetime.UTC)).astimezone(datetime.UTC)
    return now.replace(minute=0, second=0, microsecond=0)


def month_window_start(now: datetime.datetime | None = None) -> datetime.datetime:
    """Start of the current calendar UTC month."""
    now = (now or datetime.datetime.now(tz=datetime.UTC)).astimezone(datetime.UTC)
    return now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)


class DownloadRecord(models.Model):
    """One row per metered download that moves bytes (i.e. is within limits).

    The limit decision sums `size_kb` over the current calendar hour and month for a
    user; a NULL user is the shared anonymous bucket. Over-limit attempts are NOT
    rowed here -- they are tallied on DownloadDenial instead, so a flood of
    rejections can never bloat this table. Sizes are kilobytes (rounded up per file)
    to stay within a 4-byte integer even at the largest tier.
    """

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.CASCADE,
        related_name="download_records",
    )
    size_kb = models.IntegerField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        indexes = [
            # Per-user window sums (the hot-path limit decision).
            models.Index(fields=["user", "created_at"], name="dlrecord_user_created"),
            # Cross-user aggregation (e.g. by day, to reconcile with the AWS bill)
            # and the retention prune, both of which range on time alone.
            models.Index(fields=["created_at"], name="dlrecord_created"),
        ]

    def __str__(self):
        who = "anonymous" if self.user_id is None else self.user.username
        return f"DownloadRecord({who}, {self.size_kb} KB)"


class DownloadDenial(models.Model):
    """Per-(user, hour) tally of downloads that would be / are denied.

    Denials collapse into counters rather than rows: a client hammering a rejected
    endpoint a million times an hour increments one row instead of inserting a
    million. `size_kb` accumulates the would-be (observe mode) or avoided
    (enforcement) bytes, so overrun is quantifiable and reconcilable against the AWS
    bill. There is deliberately no unique constraint -- a boundary race may create a
    duplicate (user, window) row, which is harmless because reads aggregate.
    """

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.CASCADE,
        related_name="download_denials",
    )
    window = models.CharField(max_length=13)  # UTC hour, "YYYY-MM-DD-HH"
    count = models.IntegerField(default=0)
    size_kb = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        indexes = [
            # Upsert lookup on the hot path.
            models.Index(fields=["user", "window"], name="dldenial_user_window"),
            # Retention prune ranges on time alone.
            models.Index(fields=["created_at"], name="dldenial_created"),
        ]

    def __str__(self):
        who = "anonymous" if self.user_id is None else self.user.username
        return f"DownloadDenial({who}, {self.window}, {self.count})"
