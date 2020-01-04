import logging

from django.db import models

from aiarena.settings import ELO_START_VALUE
from .bot import Bot
from .season import Season
from ..storage import OverwriteStorage
from ..validators import validate_not_nan, validate_not_inf

logger = logging.getLogger(__name__)


def elo_graph_upload_to(instance, filename):
    return '/'.join(['graphs', f'{instance.season_id}_{instance.bot.id}_{instance.bot.name}.png'])


class SeasonParticipation(models.Model):
    season = models.ForeignKey(Season, on_delete=models.CASCADE)
    bot = models.ForeignKey(Bot, on_delete=models.CASCADE)
    elo = models.SmallIntegerField(default=ELO_START_VALUE)
    win_perc = models.FloatField(blank=True, null=True, validators=[validate_not_nan, validate_not_inf])
    crash_perc = models.FloatField(blank=True, null=True, validators=[validate_not_nan, validate_not_inf])
    game_count = models.IntegerField(default=0)
    elo_graph = models.FileField(upload_to=elo_graph_upload_to, storage=OverwriteStorage(), blank=True, null=True)
