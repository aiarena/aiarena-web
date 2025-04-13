from django.core.management.base import BaseCommand
from django.db.models import Q

from aiarena.core.models import Result


class Command(BaseCommand):
    help = "Removed orphaned results from the database"

    def add_arguments(self, parser):
        parser.add_argument("--dry-run", action="store_true", help="Perform a dry run without deleting any results")

    def handle(self, *args, **options):
        dry_run = options["dry_run"]

        # Get results where no associated match exists
        orphaned_results = Result.objects.filter(~Q(match__isnull=False))

        for result in orphaned_results:
            self.stdout.write(f"Orphaned result: {result}")
            if not dry_run:
                result.delete()
                self.stdout.write(f"Deleted orphaned result: {result}")
            else:
                self.stdout.write(f"Would delete orphaned result: {result}")
