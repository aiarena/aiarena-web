import datetime

from django.conf import settings
from django.core.management.base import BaseCommand

from aiarena.core.models import DownloadDenial, DownloadRecord


def retention_cutoff(now: datetime.datetime, months: int) -> datetime.datetime:
    """Start of the UTC calendar month `months - 1` months before `now`'s month, so
    the current month plus the preceding `months - 1` months are retained in full."""
    now = now.astimezone(datetime.UTC)
    total = (now.year * 12 + now.month - 1) - (months - 1)
    year, month = divmod(total, 12)
    return datetime.datetime(year, month + 1, 1, tzinfo=datetime.UTC)


class Command(BaseCommand):
    help = "Delete download accounting rows older than DOWNLOAD_RECORD_RETENTION_MONTHS."

    def handle(self, *args, **options):
        cutoff = retention_cutoff(
            datetime.datetime.now(tz=datetime.UTC),
            settings.DOWNLOAD_RECORD_RETENTION_MONTHS,
        )
        records, _ = DownloadRecord.objects.filter(created_at__lt=cutoff).delete()
        denials, _ = DownloadDenial.objects.filter(created_at__lt=cutoff).delete()
        self.stdout.write(f"Pruned {records} download records and {denials} denial counters before {cutoff:%Y-%m-%d}.")
