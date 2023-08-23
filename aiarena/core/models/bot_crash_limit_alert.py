from django.db import models

from .match_participation import MatchParticipation


class BotCrashLimitAlert(models.Model):
    """An alert logged when bots surpass the consecutive crash limit."""

    logged_at = models.DateTimeField(auto_now_add=True, blank=True)
    triggering_match_participation = models.OneToOneField(MatchParticipation, on_delete=models.CASCADE)
