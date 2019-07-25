from django.core.management.base import BaseCommand
from django.db import connection


class Command(BaseCommand):
    help = "Runs the generate stats db routine to generate bot stats."

    def handle(self, *args, **options):
        self.stdout.write('Generating stats...')
        with connection.cursor() as c:
            c.callproc("generate_stats")
        self.stdout.write('Done')
