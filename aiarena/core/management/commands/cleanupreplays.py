from datetime import timedelta

from django.core.management.base import BaseCommand
from django.db import transaction
from django.utils import timezone

from aiarena.core.models import Result


class Command(BaseCommand):
    help = "Cleanup and remove old replay files."

    _DEFAULT_DAYS_LOOKBACK = 30

    def add_arguments(self, parser):
        parser.add_argument('--days', type=int,
                            help="Number of days into the past to start cleaning from. Default is {0}.".format(
                                self._DEFAULT_DAYS_LOOKBACK))

    def handle(self, *args, **options):
        if options['days'] is not None:
            days = options['days']
        else:
            days = self._DEFAULT_DAYS_LOOKBACK
        self.stdout.write('Cleaning up replays starting from {0} days into the past...'.format(days))
        self.stdout.write('Cleaned up {0} replays.'.format(self.cleanup_replays(days)))

    @transaction.atomic()
    def cleanup_replays(self, days):
        results = Result.objects.filter(replay_file__isnull=False, created__lt=timezone.now() - timedelta(days=days)).select_for_update()
        for result in results:
            result.replay_file.delete()
            result.replay_file_has_been_cleaned = True
        return results.count()
