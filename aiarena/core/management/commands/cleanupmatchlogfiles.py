from datetime import timedelta

from django.db import transaction
from django.utils import timezone

from aiarena.core.management.commands.basefilecleanupcommand import BaseFileCleanupCommand
from aiarena.core.models import MatchParticipation


class Command(BaseFileCleanupCommand):
    help = "Cleanup and remove old match logfiles."

    _DEFAULT_DAYS_LOOKBACK = 30

    def _perform_cleanup(self, days, verbose):
        self.stdout.write(f"Cleaning up match logfiles starting from {days} days into the past...")
        self.stdout.write("Gathering records to clean...")
        participants = MatchParticipation.objects.exclude(match_log="").filter(
            match__result__created__lt=timezone.now() - timedelta(days=days)
        )
        self.stdout.write(f"{participants.count()} records gathered.")
        cleanup_count = 0
        for participant in participants:
            with transaction.atomic():
                participant.lock_me()
                if participant.clean_match_log():
                    participant.save()
                    cleanup_count += 1
                    if verbose:
                        self.stdout.write(f"Participant {participant.id} match log deleted.")
        self.stdout.write(f"Cleaned up {cleanup_count} logfiles.")
