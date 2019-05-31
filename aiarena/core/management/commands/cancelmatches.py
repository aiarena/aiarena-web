from django.core.management.base import BaseCommand, CommandError

from aiarena.core.models import Match, Result


class Command(BaseCommand):
    help = 'Registers an InitializationError result for all current matches.'

    def add_arguments(self, parser):
        parser.add_argument('match_ids', nargs='+', type=int)

    def handle(self, *args, **options):
        for match_id in options['match_ids']:
            try:
                match = Match.objects.get(pk=match_id)
            except Match.DoesNotExist:
                raise CommandError('Match "%s" does not exist' % match_id)

            if Result.objects.filter(match=match).count() > 0:
                raise CommandError('A result already exists for match "%s"' % match_id)

            Result.objects.create(match=match, type='InitializationError', duration=0)

            self.stdout.write(self.style.SUCCESS('Successfully marked match "%s" with an InitializationError' % match_id))