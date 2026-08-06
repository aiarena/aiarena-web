import logging

from django.db import models

from .bot import Bot
from .trophy_icon import TrophyIcon
from .competition import Competition

logger = logging.getLogger(__name__)


TROPHY_CONDITIONS = (
    ("first_place", "1st Place"),
    ("second_place", "2nd Place"),
    ("third_place", "3rd Place"),
    ("top_5", "Top 5"),
    ("top_10", "Top 10"),
    ("top_15", "Top 15"),
    ("top_20", "Top 20"),
    ("participant", "Participant"),
    ("custom", "Custom"),
)


class Trophy(models.Model):
    icon = models.ForeignKey(TrophyIcon, on_delete=models.SET_NULL, blank=True, null=True)
    bot = models.ForeignKey(Bot, on_delete=models.CASCADE, related_name="trophies")
    name = models.CharField(max_length=64)

    competition = models.ForeignKey(
        Competition,
        on_delete=models.PROTECT,
        related_name="trophies",
        blank=True,
        null=True,
    )

    condition = models.CharField(
        max_length=64,
        choices=TROPHY_CONDITIONS,
        blank=True,
    )
