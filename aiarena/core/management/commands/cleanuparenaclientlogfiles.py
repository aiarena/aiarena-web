from datetime import timedelta

from django.core.management.base import BaseCommand
from django.utils import timezone

from aiarena.core.models import Participant, Match, Result


class Command(BaseCommand):
    help = "Cleanup and remove old arena client logfiles."

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
        self.stdout.write('Cleaning up arena client logfiles starting from {0} days into the past...'.format(days))
        self.stdout.write('Cleaned up {0} logfiles.'.format(self.cleanup_logfiles(days)))

    def cleanup_logfiles(self, days):
        results = Result.objects.filter(arenaclient_log__isnull=False,
                                        created__lt=timezone.now() - timedelta(days=days))
        for result in results:
            result.arenaclient_log.delete()
        return results.count()
