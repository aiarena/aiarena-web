from datetime import timedelta

from django.db import transaction
from django.utils import timezone

from aiarena.core.management.commands.basefilecleanupcommand import BaseFileCleanupCommand
from aiarena.core.models import Result


class Command(BaseFileCleanupCommand):
    help = "Cleanup and remove old result files - replays and arena client logs."

    _DEFAULT_DAYS_LOOKBACK = 30

    def _perform_cleanup(self, days, verbose):
        self.stdout.write(f"Cleaning up result files starting from {days} days into the past...")
        self.stdout.write("Gathering records to clean...")
        # exclude results if that have neither a replay file nor an arena client log file
        results = Result.objects.exclude(replay_file="", arenaclient_log="").filter(
            created__lt=timezone.now() - timedelta(days=days)
        )
        self.stdout.write(f"{results.count()} records gathered.")
        replays_cleaned_count = ac_logs_cleaned_count = 0
        for result in results:
            with transaction.atomic():
                result.lock_me()
                change_made = False
                if result.clean_replay_file():
                    replays_cleaned_count += 1
                    change_made = True
                    if verbose:
                        self.stdout.write(f"Match {result.match_id} replay file deleted.")
                if result.clean_arenaclient_log():
                    ac_logs_cleaned_count += 1
                    change_made = True
                    if verbose:
                        self.stdout.write(f"Match {result.match_id} arenaclient log deleted.")
                if change_made:
                    result.save()
        self.stdout.write(f"Cleaned up {replays_cleaned_count} replays and {ac_logs_cleaned_count} arena client logs.")
