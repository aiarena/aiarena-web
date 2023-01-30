import datetime
from typing import List

from django.core.management.base import BaseCommand
from django.db import transaction

from aiarena.api.arenaclient.util import get_winner_loser, apply_elo_delta, \
    get_competition_participant_bot_id
from aiarena.core.models import Match, Competition, CompetitionParticipation, MatchParticipation
from aiarena.settings import ELO_START_VALUE, ELO


def fetch_sp_by_bot_id(bot_id: int, competition_participants: List[CompetitionParticipation]):
    for cp in competition_participants:
        if cp.bot_id == bot_id:
            return cp
    raise 'Competition participation for bot id not found!'


class Command(BaseCommand):
    help = 'Recalculates a competition\'s ELOs based on all matches for that competition. This can take a VERY long time. ' \
           'WARNING! Nothing else should attempt to modify the database while this runs.'

    def add_arguments(self, parser):
        parser.add_argument('competition_id', type=int, help="The competition to recalculate.")
        parser.add_argument('--dryrun', action='store_true', help="Run analysis without making changes.")

    def handle(self, *args, **options):
        dryrun = options['dryrun']
        self.stdout.write(f"Starting ELO re-calculation for competition id {options['competition_id']}...")
        started_at = datetime.datetime.now()
        self.stdout.write(f"Started at: {started_at}")
        with transaction.atomic():
            self.stdout.write(f"Locking records...")
            target_competition = Competition.objects.select_for_update().get(id=options['competition_id'])
            self.stdout.write(f"Competition id {target_competition.id} locked.")
            competition_participants = CompetitionParticipation.objects.select_for_update().filter(competition=target_competition)
            self.stdout.write(f"{competition_participants.count()} competition participants locked.")
            matches = Match.objects.select_for_update().filter(round__competition=target_competition, result__isnull=False)\
                .prefetch_related('matchparticipation_set', 'result').order_by('result__created')

            self.stdout.write(f"{matches.count()} matches locked.")

            self.stdout.write(f"Resetting all ELOs to starting ELO...", ending='\r')
            for participant in competition_participants:
                participant.starting_elo = participant.elo  # save the old elo for comparison
                participant.elo = ELO_START_VALUE
            self.stdout.write(f"Resetting all ELOs to starting ELO...done")

            self.stdout.write(f"Recalculating all match ELOs...0%", ending='\r')
            count: int = 0
            for match in matches:
                count += 1
                p1: MatchParticipation = match.participant1
                p2: MatchParticipation = match.participant2

                sp1 = fetch_sp_by_bot_id(get_competition_participant_bot_id(match_id=match.id, participant_number=1),
                                         competition_participants)
                sp2 = fetch_sp_by_bot_id(get_competition_participant_bot_id(match_id=match.id, participant_number=2),
                                         competition_participants)

                # Update and record ELO figures
                p1_initial_elo = sp1.elo
                p2_initial_elo = sp2.elo
                initial_elo_sum = p1_initial_elo + p2_initial_elo

                if match.result.has_winner:
                    sp_winner, sp_loser = get_winner_loser(match.result.type, sp1, sp2)
                    apply_elo_delta(ELO.calculate_elo_delta(sp_winner.elo, sp_loser.elo, 1.0), sp_winner,
                                    sp_loser)
                elif match.result.type == 'Tie':
                    apply_elo_delta(ELO.calculate_elo_delta(sp1.elo, sp2.elo, 0.5), sp1,
                                    sp2)

                # Calculate the change in ELO
                p1.resultant_elo = sp1.elo
                p2.resultant_elo = sp2.elo
                p1.elo_change = p1.resultant_elo - p1_initial_elo
                p2.elo_change = p2.resultant_elo - p2_initial_elo

                if not dryrun:
                    p2.save()
                    p2.save()

                resultant_elo_sum = p1.resultant_elo + p2.resultant_elo
                if initial_elo_sum != resultant_elo_sum:
                    self.stdout.write(f"ERROR: Initial and resultant ELO sum mismatch: "
                                    f"Match {match.id}. "
                                    f"initial_elo_sum: {initial_elo_sum}. "
                                    f"resultant_elo_sum: {resultant_elo_sum}. "
                                    f"participant1.elo_change: {p1.elo_change}. "
                                    f"participant2.elo_change: {p2.elo_change}")

                self.stdout.write(f"Recalculating all match ELOs...{count/matches.count()*100:.2f}%", ending='\r')

            self.stdout.write("bot_id starting_elo ending_elo elo_change")
            for participant in competition_participants:
                elo_change = participant.elo-participant.starting_elo
                self.stdout.write(f"{participant.bot_id:>6}{participant.starting_elo:>13}{participant.elo:>11}{elo_change:>11}")

                if not dryrun:
                    participant.save()

        self.stdout.write(f"Recalculating all match ELOs...done")
        self.stdout.write(f"Job finished!")
        finished_at = datetime.datetime.now()
        self.stdout.write(f"Finished at: {finished_at}")
        self.stdout.write(f"Elapsed seconds: {(finished_at-started_at).total_seconds()}")
