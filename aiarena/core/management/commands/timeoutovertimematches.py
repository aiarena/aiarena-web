from django.core.management.base import BaseCommand, CommandError
from django.db import transaction

from aiarena.core.api import Matches


class Command(BaseCommand):
    help = 'Time out any matches that have run overtime.'

    def handle(self, *args, **options):
        with transaction.atomic():
            Matches.timeout_overtime_bot_games()
