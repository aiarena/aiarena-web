import logging

from django.db import models

from aiarena.core.models import Bot
from aiarena.core.validators import validate_not_nan, validate_not_inf
# from .season_participation import SeasonParticipation

logger = logging.getLogger(__name__)


class SeasonBotMatchupStats(models.Model):
    bot = None  # Dan ,  the DB expects bot_id to be in this table,  any suggestions ?
    opponent = None
    bot1 = models.ForeignKey(Bot, on_delete=models.CASCADE, related_name='bot1')
    bot2 = models.ForeignKey(Bot, on_delete=models.CASCADE, related_name='bot2')
    match_count = models.IntegerField(blank=True, null=True)
    win_count = models.IntegerField(blank=True, null=True)
    win_perc = models.FloatField(blank=True, null=True, validators=[validate_not_nan, validate_not_inf])
    loss_count = models.IntegerField(blank=True, null=True)
    loss_perc = models.FloatField(blank=True, null=True, validators=[validate_not_nan, validate_not_inf])
    tie_count = models.IntegerField(blank=True, null=True)
    tie_perc = models.FloatField(blank=True, null=True, validators=[validate_not_nan, validate_not_inf])
    crash_count = models.IntegerField(blank=True, null=True)
    crash_perc = models.FloatField(blank=True, null=True, validators=[validate_not_nan, validate_not_inf])
