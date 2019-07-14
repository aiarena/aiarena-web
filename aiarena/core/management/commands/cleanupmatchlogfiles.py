from datetime import timedelta

from django.core.management.base import BaseCommand
from django.utils import timezone

from aiarena.core.models import Participant


class Command(BaseCommand):
    help = "Cleanup and remove old match logfiles."

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
        self.stdout.write('Cleaning up match logfiles starting from {0} days into the past...'.format(days))
        self.stdout.write('Cleaned up {0} logfiles.'.format(self.cleanup_logfiles(days)))

    def cleanup_logfiles(self, days):
        participants = Participant.objects.filter(match_log__isnull=False,
                                                  match__result__created__lt=timezone.now() - timedelta(days=days))
        for participant in participants:
            participant.match_log.delete()
        return participants.count()
