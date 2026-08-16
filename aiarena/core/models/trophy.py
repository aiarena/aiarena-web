import logging

from django.db import models

from .bot import Bot
from .competition_participation import CompetitionParticipation
from .trophy_icon import TrophyIcon


logger = logging.getLogger(__name__)


class TrophyCondition(models.TextChoices):
    FIRST_PLACE = "first_place", "1st Place"
    SECOND_PLACE = "second_place", "2nd Place"
    THIRD_PLACE = "third_place", "3rd Place"

    TOP_5 = "top_5", "Top 5"
    TOP_10 = "top_10", "Top 10"
    TOP_15 = "top_15", "Top 15"
    TOP_20 = "top_20", "Top 20"

    BEST_ZERG = "best_zerg", "Best Zerg"
    BEST_PROTOSS = "best_protoss", "Best Protoss"
    BEST_TERRAN = "best_terran", "Best Terran"
    BEST_RANDOM = "best_random", "Best Random"

    PARTICIPANT = "participant", "Participant"
    CUSTOM = "custom", "Custom"


class Trophy(models.Model):
    """An award given to a bot, optionally tied to a competition participation."""

    icon = models.ForeignKey(
        TrophyIcon,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
    )

    bot = models.ForeignKey(
        Bot,
        on_delete=models.CASCADE,
        related_name="trophies",
    )

    name = models.CharField(
        max_length=64,
    )

    competition_participation = models.ForeignKey(
        CompetitionParticipation,
        on_delete=models.SET_NULL,
        related_name="trophies",
        blank=True,
        null=True,
    )


    condition = models.CharField(
        max_length=64,
        choices=TrophyCondition.choices,
        blank=True,
    )

    def __str__(self):
        return self.name