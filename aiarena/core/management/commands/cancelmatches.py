from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from aiarena.core.models import Match


class Command(BaseCommand):
    help = 'Registers a MatchCancelled result for all current matches.'

    def add_arguments(self, parser):
        parser.add_argument('match_ids', nargs='+', type=int)

    def handle(self, *args, **options):
        with transaction.atomic():
            for match_id in options['match_ids']:
                try:
                    match = Match.objects.select_for_update().get(pk=match_id)
                except Match.DoesNotExist:
                    raise CommandError('Match "%s" does not exist' % match_id)

                cancel_result = match.cancel()

                if cancel_result == Match.CancelResult.SUCCESS:
                    self.stdout.write(
                        self.style.SUCCESS('SUCCESS: Marked match "%s" with a MatchCancelled result.' % match_id))
                elif cancel_result == Match.CancelResult.FAIL_ALREADY_HAS_RESULT:
                    self.stdout.write(
                        self.style.SUCCESS('FAIL: Match "%s" already has a result.' % match_id))
                else:
                    self.stdout.write(
                        self.style.SUCCESS('FAIL: Could not cancel match "%s" due to unknown reason.' % match_id))
