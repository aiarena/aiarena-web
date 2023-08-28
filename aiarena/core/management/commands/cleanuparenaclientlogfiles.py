from datetime import timedelta

from django.core.management.base import BaseCommand
from django.db import transaction
from django.utils import timezone

from aiarena.core.models import Result


class Command(BaseCommand):
    help = "Cleanup and remove old arena client logfiles."

    _DEFAULT_DAYS_LOOKBACK = 30

    def add_arguments(self, parser):
        parser.add_argument(
            "--days",
            type=int,
            help=f"Number of days into the past to start cleaning from. Default is {self._DEFAULT_DAYS_LOOKBACK}.",
        )
        parser.add_argument("--verbose", action="store_true", help="Output information with each action.")

    def handle(self, *args, **options):
        if options["days"] is not None:
            days = options["days"]
        else:
            days = self._DEFAULT_DAYS_LOOKBACK
        self.stdout.write(f"Cleaning up arena client logfiles starting from {days} days into the past...")
        cleaned = self.cleanup_logfiles(days, options["verbose"])
        self.stdout.write(f"Cleaned up {cleaned} logfiles.")

    def cleanup_logfiles(self, days, verbose):
        self.stdout.write("Gathering records to clean...")
        results = Result.objects.exclude(arenaclient_log="").filter(created__lt=timezone.now() - timedelta(days=days))
        self.stdout.write(f"{results.count()} records gathered.")
        for result in results:
            with transaction.atomic():
                result.lock_me()
                result.arenaclient_log_has_been_cleaned = True
                result.arenaclient_log.delete()
                result.save()
                if verbose:
                    self.stdout.write(f"Match {result.match_id} arena client log deleted.")
        return results.count()
