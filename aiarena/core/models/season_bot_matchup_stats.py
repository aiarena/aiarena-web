import logging

from django.db import models
from django.utils import timezone
from aiarena.core.validators import validate_not_nan, validate_not_inf
from .season_participation import SeasonParticipation

logger = logging.getLogger(__name__)


class SeasonBotMatchupStats(models.Model):
    bot = models.ForeignKey(SeasonParticipation, on_delete=models.CASCADE, related_name='season_matchup_stats')
    opponent = models.ForeignKey(SeasonParticipation, on_delete=models.CASCADE, related_name='opponent_matchup_stats')
    match_count = models.IntegerField(blank=True, null=True)
    win_count = models.IntegerField(blank=True, null=True)
    win_perc = models.FloatField(blank=True, null=True, validators=[validate_not_nan, validate_not_inf])
    loss_count = models.IntegerField(blank=True, null=True)
    loss_perc = models.FloatField(blank=True, null=True, validators=[validate_not_nan, validate_not_inf])
    tie_count = models.IntegerField(blank=True, null=True)
    tie_perc = models.FloatField(blank=True, null=True, validators=[validate_not_nan, validate_not_inf])
    crash_count = models.IntegerField(blank=True, null=True)
    crash_perc = models.FloatField(blank=True, null=True, validators=[validate_not_nan, validate_not_inf])
    updated = models.DateTimeField(default=timezone.now)  # populate fields before first save

    def save(self, *args, **kwargs):
        # update time pre save
        self.updated = timezone.now()
        # now we call django's save protocol
        super(SeasonBotMatchupStats, self).save(*args, **kwargs)

    def __str__(self):
        return str(self.bot) + ' VS ' + str(self.opponent)
