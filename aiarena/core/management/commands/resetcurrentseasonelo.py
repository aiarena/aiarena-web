from django.core.management.base import BaseCommand

from aiarena import settings
from aiarena.core.models import Bot, SeasonParticipation, Season


class Command(BaseCommand):
    help = 'Reset all bot ELO values to the start value for the current season.'

    def handle(self, *args, **options):
        SeasonParticipation.objects.filter(season=Season.get_current_season()).update(elo=settings.ELO_START_VALUE)
        self.stdout.write("Current Season ELO values have been reset.")