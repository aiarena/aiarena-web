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
    label = models.CharField(max_length=1, choices=RACES, unique=True)

    @staticmethod
    def create_all_races():
        for race in BotRace.RACES:
            BotRace.objects.create(label=race[0])

    @staticmethod
    def terran():
        return BotRace.objects.get(label='T')

    @staticmethod
    def zerg():
        return BotRace.objects.get(label='Z')

    @staticmethod
    def protoss():
        return BotRace.objects.get(label='P')

    @staticmethod
    def random():
        return BotRace.objects.get(label='R')

    def __str__(self):
        return self.get_label_display()
