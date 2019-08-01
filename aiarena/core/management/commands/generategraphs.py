from django.core.management.base import BaseCommand
from django.db import connection


class Command(BaseCommand):
    help = 'Generates bot statistic graphs.'

    def handle(self, *args, **options):
        self.stdout.write('Generating graphs...')
        with connection.cursor() as cursor:
            # refer to https://docs.djangoproject.com/en/2.2/topics/db/sql/#executing-custom-sql-directly
            cursor.execute("SELECT * FROM whatever where id=%s", [id])
            rows = cursor.fetchall()
            # do stuff with rows
        self.stdout.write('Done')
