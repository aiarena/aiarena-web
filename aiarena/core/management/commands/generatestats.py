from django.core.management.base import BaseCommand

from aiarena.core.models import Bot
from aiarena.core.stats.stats_generator import StatsGenerator


class Command(BaseCommand):
    help = "Runs the generate stats db routine to generate bot stats."


    def add_arguments(self, parser):
        parser.add_argument('bot_id', type=int, help="The bot id to generate the stats for.")

    def handle(self, *args, **options):
        bot_id = options['bot_id']
        self.stdout.write(f'Generating stats for bot {bot_id}...')
        StatsGenerator.update_stats(Bot.objects.get(id=bot_id))
        self.stdout.write('Done')
