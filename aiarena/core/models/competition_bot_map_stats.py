import logging

from django.db import models
from django.utils import timezone
from aiarena.core.validators import validate_not_nan, validate_not_inf
from .competition_participation import CompetitionParticipation
from .map import Map

logger = logging.getLogger(__name__)


class CompetitionBotMapStats(models.Model):
    bot = models.ForeignKey(CompetitionParticipation, on_delete=models.CASCADE, related_name='competition_map_stats')
    map = models.ForeignKey(Map, on_delete=models.CASCADE)
    match_count = models.IntegerField(default=0, blank=True)
    win_count = models.IntegerField(default=0, blank=True)
    win_perc = models.FloatField(default=0, blank=True, validators=[validate_not_nan, validate_not_inf])
    loss_count = models.IntegerField(default=0, blank=True)
    loss_perc = models.FloatField(default=0, blank=True, validators=[validate_not_nan, validate_not_inf])
    tie_count = models.IntegerField(default=0, blank=True)
    tie_perc = models.FloatField(default=0, blank=True, validators=[validate_not_nan, validate_not_inf])
    crash_count = models.IntegerField(default=0, blank=True)
    crash_perc = models.FloatField(default=0, blank=True, validators=[validate_not_nan, validate_not_inf])
    updated = models.DateTimeField(default=timezone.now)  # populate fields before first save

    def save(self, *args, **kwargs):
        # update time pre save
        self.updated = timezone.now()
        # now we call django's save protocol
        super(CompetitionBotMapStats, self).save(*args, **kwargs)

    def __str__(self):
        return str(self.bot) + ' on ' + str(self.map)

    class Meta:
        unique_together = (('bot', 'map'),)
