from django.core.management.base import BaseCommand, CommandError
from django.db import transaction

from aiarena.core.models import CompetitionParticipation, Competition
from aiarena.core.api.bot_statistics import BotStatistics


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
                            help="Mark the processed competition's stats as finalized. "
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
            with transaction.atomic():
                competition.lock_me()
                if not competition.statistics_finalized:
                    if finalize:
                        competition.statistics_finalized = True
                        competition.save()
                    for sp in CompetitionParticipation.objects.filter(competition_id=competition.id):
                        sp.lock_me()
                        self.stdout.write(f'Generating current competition stats for bot {sp.bot_id}...')
                        BotStatistics.recalculate_stats(sp)
                else:
                    self.stdout.write(f'WARNING: Skipping competition {competition.id} - stats already finalized.')

        self.stdout.write('Done')
