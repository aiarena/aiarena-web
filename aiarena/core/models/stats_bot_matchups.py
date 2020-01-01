import logging

from django.db import models

from aiarena.core.validators import validate_not_nan, validate_not_inf
from .bot import Bot

logger = logging.getLogger(__name__)


# todo: rename to BotMatchupStats
class StatsBotMatchups(models.Model):
    bot = models.ForeignKey(Bot, on_delete=models.CASCADE)
    opponent = models.ForeignKey(Bot, on_delete=models.CASCADE, related_name='opponent_stats')
    win_perc = models.FloatField(validators=[validate_not_nan, validate_not_inf])
    win_count = models.IntegerField()
    game_count = models.IntegerField()
    generated_at = models.DateTimeField()
