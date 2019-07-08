from django.core.management.base import BaseCommand

from aiarena import settings
from aiarena.core.models import Bot


class Command(BaseCommand):
    help = 'Reset all bot ELO values to the start value.'

    def handle(self, *args, **options):
        Bot.objects.update(elo=settings.ELO_START_VALUE)
        self.stdout.write("ELO values have been reset.")