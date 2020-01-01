import logging

from django.db import models

from aiarena.settings import ELO_START_VALUE
from .bot import Bot
from .season import Season

logger = logging.getLogger(__name__)


class SeasonParticipation(models.Model):
    season = models.ForeignKey(Season, on_delete=models.CASCADE)
    bot = models.ForeignKey(Bot, on_delete=models.CASCADE)
    elo = models.SmallIntegerField(default=ELO_START_VALUE)
