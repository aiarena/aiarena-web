import logging

from django.db import models
from django.utils import timezone
from aiarena.core.validators import validate_not_nan, validate_not_inf
from .competition_participation import CompetitionParticipation

logger = logging.getLogger(__name__)


class CompetitionBotMatchupStats(models.Model):
    bot = models.ForeignKey(
        CompetitionParticipation, on_delete=models.CASCADE, related_name="competition_matchup_stats"
    )
    opponent = models.ForeignKey(
        CompetitionParticipation, on_delete=models.CASCADE, related_name="opponent_matchup_stats"
    )
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
        super(CompetitionBotMatchupStats, self).save(*args, **kwargs)

    def __str__(self):
        return str(self.bot) + " VS " + str(self.opponent)

    class Meta:
        unique_together = (("bot", "opponent"),)
