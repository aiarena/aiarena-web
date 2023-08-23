from django.core.management.base import BaseCommand, CommandError
from django.db import transaction

from aiarena.core.models import Competition, Round


class Command(BaseCommand):
    help = (
        "Marks a competition as finalized and purges all rounds and match data for said competition. "
        "The specified competition must be of status 'closed'"
    )

    def add_arguments(self, parser):
        parser.add_argument("--competitionid", type=int, help="The id of the competition to finalize.")

    def handle(self, *args, **options):
        with transaction.atomic():
            competition = Competition.objects.get(id=options["competitionid"])
            competition.lock_me()

            self.stdout.write(f"Attempting to finalize competition {competition.id}.")

            if competition.status == "closed":
                if not competition.competition_finalized:
                    competition.competition_finalized = True
                    competition.save()

                    rounds = Round.objects.filter(competition_id=competition.id)
                    self.stdout.write(f"Deleting {rounds.count()} rounds...")
                    rounds.delete()
                    self.stdout.write(f"Competition {competition.id} has been finalized.")
                else:
                    self.stdout.write(f"WARNING: Competition {competition.id} is already finalized. Skipping...")
            else:
                raise CommandError(
                    f"Competition {competition.id} is not closed! It must be closed before it can be finalized."
                )

        self.stdout.write("Done")
