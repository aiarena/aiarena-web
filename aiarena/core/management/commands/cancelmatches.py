from django.core.management.base import BaseCommand, CommandError

from aiarena.core.models import Match
from aiarena.core.services import matches


class Command(BaseCommand):
    help = "Registers a MatchCancelled result for all specified matches."

    def add_arguments(self, parser):
        parser.add_argument("match_ids", nargs="?", type=int, help="A space separated list of match ids to cancel.")
        parser.add_argument(
            "--active", action="store_true", help="Indicates that all active matches should be cancelled"
        )

    def handle(self, *args, **options):
        match_ids = options["match_ids"]

        if isinstance(match_ids, list):
            for match_id in match_ids:
                self.cancel(match_id)
        elif match_ids is not None:
            self.cancel(match_ids)

        if options["active"]:
            for match_id in Match.objects.filter(result__isnull=True, started__isnull=False).values_list(
                "id", flat=True
            ):
                self.cancel(match_id)

    def cancel(self, match_id):
        try:
            matches.cancel(match_id)
        except Exception as e:
            raise CommandError(e)
        self.stdout.write(self.style.SUCCESS(f'Successfully marked match "{match_id}" with MatchCancelled'))
