from django.core.management.base import BaseCommand
from django.db.models import Q

from aiarena.core.models import Result


class Command(BaseCommand):
    help = "Removed orphaned results from the database"

    def add_arguments(self, parser):
        parser.add_argument("--dry-run", action="store_true", help="Perform a dry run without deleting any results")

    def handle(self, *args, **options):
        dry_run = options["dry_run"]

        orphaned_results = Result.objects.filter(~Q(match__isnull=False))

        self.stdout.write(f"Found {orphaned_results.count()} orphaned results.")
        if dry_run:
            self.stdout.write("Dry run: No results will be deleted.")
        else:
            orphaned_results.delete()
            self.stdout.write(f"Deleted {orphaned_results.count()} orphaned results.")
