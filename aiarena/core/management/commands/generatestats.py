from django.core.management.base import BaseCommand
from django.db import transaction

from aiarena.core.models import Bot, SeasonParticipation, Season
from aiarena.core.stats.stats_generator import StatsGenerator


class Command(BaseCommand):
    help = "Runs the generate stats db routine to generate bot stats."


    def add_arguments(self, parser):
        parser.add_argument('--botid', type=int, help="The bot id to generate the stats for. "
                                                       "If this isn't supplied, all bots will have "
                                                       "their stats generated.")
        parser.add_argument('--seasonid', type=int, help="The season id t generate stats for. "
                                                       "If this isn't supplied the currently "
                                                       "active season will ne used")
        parser.add_argument('--allseasons', type=bool, help="Run this for all seasons")

    def handle(self, *args, **options):
        bot_id = options['botid']

        if options['allseasons']:
            seasons = Season.objects.all()
        else:
            seasons = [options['seasonid'] if options['seasonid'] is not None else Season.get_current_season().id]

            for s in seasons:
                season_id = s.id
                if bot_id is not None:
                    sp = SeasonParticipation.objects.get(season_id=season_id, bot_id=bot_id)
                    with transaction.atomic():
                        sp.lock_me()
                        self.stdout.write(f'Generating current season stats for bot {bot_id}...')
                        StatsGenerator.update_stats(sp)
                else:
                    for sp in SeasonParticipation.objects.filter(season_id=season_id):
                        with transaction.atomic():
                            sp.lock_me()
                            self.stdout.write(f'Generating current season stats for bot {sp.bot_id}...')
                            StatsGenerator.update_stats(sp)

        self.stdout.write('Done')
