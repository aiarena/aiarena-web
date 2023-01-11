from django.core.management.base import BaseCommand, CommandError
from django.db import transaction

from aiarena.core.models import Bot, CompetitionParticipation, Competition
from aiarena.core.stats.stats_generator import StatsGenerator


class Command(BaseCommand):
    help = "Runs the generate stats db routine to generate bot stats."


    def add_arguments(self, parser):
        parser.add_argument('--botid', type=int, help="The bot id to generate the stats for. "
                                                       "If this isn't supplied, all bots will have "
                                                       "their stats generated.")
        parser.add_argument('--competitionid', type=int, help="The competition id to generate stats for. "
                                                       "If this isn't supplied all "
                                                       "open competitions will be used")
        parser.add_argument('--allcompetitions', action='store_true', help="Run this for all competition")
        parser.add_argument('--finalize', action='store_true',
                            help="Mark all processed competitions' stats as finalized. "
                                 "Only valid when specifying --competitionid.")

    def handle(self, *args, **options):
        if options['allcompetitions']:
            competitions = Competition.objects.all()
        elif options['competitionid']:
            competitions = Competition.objects.filter(id=options['competitionid'])
        else:
            competitions = Competition.objects.filter(status__in=['open', 'closing'])

        finalize = options['finalize']
        if finalize and (options['allcompetitions'] or not options['competitionid']):
            raise CommandError("--finalize is only valid with --competitionid")

        bot_id = options['botid']
        if bot_id is not None:
            # only process competitions this bot was present for.
            competitions = competitions.filter(participations__bot_id=bot_id)

        self.stdout.write(f'looping   {len(competitions)} Competitions')
        for competition in competitions:
            # this is to avoid locking the competition for the whole job
            # if we did lock the competition, it would freeze the arena client API the entire time the stats gen ran
            # Technically this means this job can fail and the stats still be marked as final.
            # This is deemed as acceptable at this time.
            proceed_with_stats_gen = True

            with transaction.atomic():
                competition.lock_me()
                if not competition.statistics_finalized:
                    if finalize:
                        competition.statistics_finalized = True
                        competition.save()
                else:
                    proceed_with_stats_gen = False
                    self.stdout.write(f'WARNING: Skipping competition {competition.id} - stats already finalized.')

            if proceed_with_stats_gen:
                for sp in CompetitionParticipation.objects.filter(competition_id=competition.id):
                    with transaction.atomic():
                        sp.lock_me()
                        self.stdout.write(f'Generating current competition stats for bot {sp.bot_id}...')
                        StatsGenerator.update_stats(sp)

        self.stdout.write('Done')
