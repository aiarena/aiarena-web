from django.core.management.base import BaseCommand
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

    def handle(self, *args, **options):
        if options['allcompetitions']:
            competitions = Competition.objects.all()
        elif options['competitionid']:
            competitions = Competition.objects.filter(id=options['competitionid'])
        else:
            competitions = Competition.objects.filter(status__in=['open', 'closing'])

        bot_id = options['botid']
        if bot_id is not None:
            # only process competitions this bot was present for.
            competitions = competitions.filter(participations__bot_id=bot_id)

        self.stdout.write(f'looping   {len(competitions)} Competitions')
        for competition in competitions:
            for sp in CompetitionParticipation.objects.filter(competition_id=competition.id):
                with transaction.atomic():
                    sp.lock_me()
                    self.stdout.write(f'Generating current competition stats for bot {sp.bot_id}...')
                    StatsGenerator.update_stats(sp)

        self.stdout.write('Done')
