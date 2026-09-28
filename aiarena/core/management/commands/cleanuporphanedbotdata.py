from datetime import timedelta

from django.core.management import BaseCommand
from django.utils import timezone

from aiarena.core.models import Bot


class Command(BaseCommand):
    help = "Delete bot_data files in storage that are no longer referenced by their bot. Dry run unless --delete."

    _DEFAULT_MIN_AGE_MINUTES = 60

    def add_arguments(self, parser):
        parser.add_argument("--delete", action="store_true", help="Actually delete files. Without it, only report.")
        parser.add_argument(
            "--min-age-minutes",
            type=int,
            default=self._DEFAULT_MIN_AGE_MINUTES,
            help="Skip files newer than this, so an in-flight upload whose DB update hasn't committed yet is kept. "
            f"Default is {self._DEFAULT_MIN_AGE_MINUTES}.",
        )
        parser.add_argument("--verbose", action="store_true", help="Output information with each file.")

    def handle(self, *args, **options):
        delete = options["delete"]
        verbose = options["verbose"]
        cutoff = timezone.now() - timedelta(minutes=options["min_age_minutes"])
        storage = Bot._meta.get_field("bot_data").storage

        if not delete:
            self.stdout.write("Dry run - no files will be deleted. Pass --delete to delete them.")

        orphan_count = 0
        for bot_id, current_name in Bot.objects.values_list("id", "bot_data").iterator():
            bot_dir = f"bots/{bot_id}"
            try:
                _, files = storage.listdir(bot_dir)
            except FileNotFoundError:  # filesystem storage, bot without any files
                continue
            for filename in files:
                name = f"{bot_dir}/{filename}"
                if not filename.startswith("bot_data") or name == current_name:
                    continue
                if storage.get_modified_time(name) > cutoff:
                    continue

                orphan_count += 1
                if verbose:
                    self.stdout.write(f"Orphaned: {name}")
                if delete:
                    storage.delete(name)

        verb = "Deleted" if delete else "Found"
        self.stdout.write(f"{verb} {orphan_count} orphaned bot_data files.")
