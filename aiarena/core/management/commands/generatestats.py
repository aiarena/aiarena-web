from django.core.management.base import BaseCommand, CommandError
from django.db import transaction

from django_pglocks import advisory_lock

from aiarena.core.models import Competition, CompetitionParticipation
from aiarena.core.services.bot_statistics import BotStatistics


class Command(BaseCommand):
    help = "Runs the generate stats db routine to generate bot stats."

    def add_arguments(self, parser):
        parser.add_argument(
            "--botid",
            type=int,
            help="The bot id to generate the stats for. "
            "If this isn't supplied, all bots will have "
            "their stats generated.",
        )
        parser.add_argument(
            "--competitionid",
            type=int,
            help="The competition id to generate stats for. If this isn't supplied all open competitions will be used",
        )
        parser.add_argument("--allcompetitions", action="store_true", help="Run this for all competition")
        parser.add_argument(
            "--finalize",
            action="store_true",
            help="Mark the processed competition's stats as finalized. Only valid when specifying --competitionid.",
        )
        parser.add_argument(
            "--graphsonly",
            action="store_true",
            help="Generate only ELO graphs. Not valid with --finalize. ",
        )

    def handle(self, *args, **options):
        if options["allcompetitions"]:
            competitions = Competition.objects.all()
        elif options["competitionid"]:
            competitions = Competition.objects.filter(id=options["competitionid"])
        else:
            competitions = Competition.objects.filter(status__in=["open", "closing"])

        finalize = options["finalize"]
        if finalize and (options["allcompetitions"] or not options["competitionid"]):
            raise CommandError("--finalize is only valid with --competitionid")

        graphs_only = options["graphsonly"]
        if graphs_only and finalize:
            raise CommandError("--graphsonly is not valid with --finalize")

        bot_id = options["botid"]
        if bot_id is not None:
            # only process competitions this bot was present for.
            competitions = competitions.filter(participations__bot_id=bot_id)

        self.stdout.write(f"looping {len(competitions)} Competitions")
        for competition in competitions:
            if finalize:
                self.stdout.write(f"Finalizing stats for competition {competition.id}...")
                with transaction.atomic():
                    # This lock will be held for a long time.
                    # This is considered acceptable as we only finalize old competitions,
                    # so no matches should be running. We also need all bot stats data to be successfully
                    # regenerated before we can finalize the competition, else it could end up finalized in a corrupted
                    # state.
                    competition.lock_me()
                    self._run_generate_stats(competition, finalize=True)
            else:
                self._run_generate_stats(competition, graphs_only=graphs_only)

        self.stdout.write("Done")

    def _run_generate_stats(self, competition, finalize=False, graphs_only=False):
        if competition.statistics_finalized:
            self.stdout.write(f"WARNING: Skipping competition {competition.id} - stats already finalized.")

        if finalize:
            competition.statistics_finalized = True
            competition.save()

        with advisory_lock(f"stats_lock_competition_{competition.id}") as acquired:
            if not acquired:
                raise Exception(f"Could not acquire lock on bot statistics for competition {str(competition.id)}")
            for sp in CompetitionParticipation.objects.filter(competition_id=competition.id):
                self.stdout.write(f"Generating current competition stats for bot {sp.bot_id}...")
                if graphs_only:
                    BotStatistics().generate_graphs(sp)
                else:
                    BotStatistics().recalculate_stats(sp)
