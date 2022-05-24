import logging

from django.db import models

logger = logging.getLogger(__name__)


class BotRace(models.Model):
    RACES = (
        ('T', 'Terran'),
        ('Z', 'Zerg'),
        ('P', 'Protoss'),
        ('R', 'Random'),
    )
    label = models.CharField(max_length=1, choices=RACES)

    @staticmethod
    def create_all_races():
        for race in BotRace.RACES:
            BotRace.objects.create(label=race[0])
