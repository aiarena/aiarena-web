from django.conf import settings
from django.core.management.base import BaseCommand

from aiarena.core.models import Competition, CompetitionParticipation, Match, MatchParticipation


class Command(BaseCommand):
    help = (
        "Recalculates a competition's ELOs based on all matches for that competition. "
        "This can take a VERY long time. "
        "WARNING: This is not protected by a lock or transaction. "
        "Ensure no other processes are affecting this competition while this job runs."
    )

    def add_arguments(self, parser):
        parser.add_argument("competition_id", type=int, help="The competition to recalculate.")

    def handle(self, *args, **options):
        self.stdout.write(f"Starting ELO re-calculation for competition id {options['competition_id']}...")
        target_competition = Competition.objects.get(id=options["competition_id"])
        self.stdout.write(f"Competition id {target_competition.id} located.")
        competition_participants = CompetitionParticipation.objects.filter(competition=target_competition)
        self.stdout.write(f"{competition_participants.count()} competition participants located.")
        matches = (
            Match.objects.filter(round__competition=target_competition, result__isnull=False)
            .prefetch_related("matchparticipation_set", "result")
            .order_by("result__created")
        )

        self.stdout.write(f"{matches.count()} matches located.")

        self.stdout.write("Resetting all ELOs to starting ELO...", ending="\r")
        for participant in competition_participants:
            participant.elo = settings.ELO_START_VALUE
            participant.save()
        self.stdout.write("Resetting all ELOs to starting ELO...done")

        self.stdout.write("Recalculating all match ELOs...0%", ending="\r")
        count: int = 0
        for match in matches:
            count += 1
            p1: MatchParticipation = match.participant1
            p2: MatchParticipation = match.participant2

            # Starting ELO
            p1_starting_elo = p1.competition_participant.elo
            p2_starting_elo = p2.competition_participant.elo
            initial_elo_sum = p1_starting_elo + p2_starting_elo

            match.result.adjust_elo()
            p1.competition_participant.refresh_from_db()
            p2.competition_participant.refresh_from_db()

            # Resultant ELO
            p1.resultant_elo = p1.competition_participant.elo
            p2.resultant_elo = p2.competition_participant.elo
            resultant_elo_sum = p1.resultant_elo + p2.resultant_elo

            # ELO change
            p1.elo_change = p1.resultant_elo - p1_starting_elo
            p2.elo_change = p2.resultant_elo - p2_starting_elo

            p1.save()
            p2.save()

            if initial_elo_sum != resultant_elo_sum:
                self.stdout.write(
                    f"ERROR: Initial and resultant ELO sum mismatch: "
                    f"Match {match.id}. "
                    f"initial_elo_sum: {initial_elo_sum}. "
                    f"resultant_elo_sum: {resultant_elo_sum}. "
                    f"participant1.elo_change: {p1.elo_change}. "
                    f"participant2.elo_change: {p2.elo_change}"
                )

            self.stdout.write(f"Recalculating all match ELOs...{count / matches.count() * 100}%", ending="\r")

        self.stdout.write("Recalculating all match ELOs...done")
        self.stdout.write("Job finished!")
