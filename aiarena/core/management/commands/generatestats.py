from django.core.management.base import BaseCommand

from aiarena.core.stats.stats_generator import StatsGenerator


class Command(BaseCommand):
    help = "Runs the generate stats db routine to generate bot stats."

    def handle(self, *args, **options):
        self.stdout.write('Generating stats...')
        StatsGenerator.generate_stats()
        self.stdout.write('Done')
