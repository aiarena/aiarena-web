import logging

from django.db import models

from aiarena.core.storage import OverwriteStorage
from aiarena.core.validators import validate_not_nan, validate_not_inf
from .bot import Bot

logger = logging.getLogger(__name__)


def elo_graph_upload_to(instance, filename):
    return '/'.join(['graphs', '{0}_{1}.png'.format(instance.bot.id, instance.bot.name)])


# todo: rename to BotStats
class StatsBots(models.Model):
    bot = models.ForeignKey(Bot, on_delete=models.CASCADE)
    win_perc = models.FloatField(validators=[validate_not_nan, validate_not_inf])
    crash_perc = models.FloatField(validators=[validate_not_nan, validate_not_inf])
    game_count = models.IntegerField()
    generated_at = models.DateTimeField()
    elo_graph = models.FileField(upload_to=elo_graph_upload_to, storage=OverwriteStorage(), blank=True,
                                 null=True)
