from datetime import timedelta

from django.core.management import BaseCommand
from django.utils import timezone

from aiarena.core.models import MatchParticipation, Result


class Command(BaseCommand):
    help = "Cleanup and remove old match logfiles."

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
        self._perform_cleanup(days, options["verbose"])

    def _perform_cleanup(self, days, verbose):
        self.stdout.write(f"Cleaning up result files starting from {days} days into the past...")
        self.stdout.write("Gathering records to clean...")
        # exclude results if that have neither a replay file nor an arena client log file
        results = Result.objects.exclude(replay_file="", arenaclient_log="").filter(
            created__lt=timezone.now() - timedelta(days=days)
        )
        self.stdout.write(f"{results.count()} records gathered.")
        replays_cleaned_count = ac_logs_cleaned_count = 0
        processed_count = 0
        for result in results:
            change_made = False
            if result.clean_replay_file():
                replays_cleaned_count += 1
                change_made = True
                if verbose:
                    self.stdout.write(f"Match {result.match.id} replay file deleted.")
            if result.clean_arenaclient_log():
                ac_logs_cleaned_count += 1
                change_made = True
                if verbose:
                    self.stdout.write(f"Match {result.match.id} arenaclient log deleted.")
            if change_made:
                result.save()
            else:
                self.stdout.write(
                    f"WARNING: Match {result.match.id} had no files to clean up even though it should have."
                )
            processed_count += 1
            self.stdout.write(
                f"\rProgress: {processed_count}/{results.count()}",
                ending="",
            )
        self.stdout.write("\n")
        self.stdout.write(f"Cleaned up {replays_cleaned_count} replays and {ac_logs_cleaned_count} arena client logs.")

        self.stdout.write(f"Cleaning up match logfiles starting from {days} days into the past...")
        self.stdout.write("Gathering records to clean...")
        participants = MatchParticipation.objects.exclude(match_log="").filter(
            match__result__created__lt=timezone.now() - timedelta(days=days)
        )
        self.stdout.write(f"{participants.count()} records gathered.")
        cleanup_count = 0
        for participant in participants:
            if participant.clean_match_log():
                participant.save()
                cleanup_count += 1
                if verbose:
                    self.stdout.write(f"Participant {participant.id} match log deleted.")
            self.stdout.write(
                f"\rProgress: {cleanup_count}/{participants.count()}",
                ending="",
            )
        self.stdout.write("\n")
        self.stdout.write(f"Cleaned up {cleanup_count} logfiles.")
