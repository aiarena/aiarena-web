# award_set_item.py

import logging

from django.db import models

from .award_set import AwardSet
from .trophy_icon import TrophyIcon
from .trophy import TROPHY_CONDITIONS

logger = logging.getLogger(__name__)


class AwardSetItem(models.Model):
    award_set = models.ForeignKey(
        AwardSet,
        on_delete=models.CASCADE,
        related_name="items",
    )
    condition = models.CharField(
        max_length=32,
        choices=TROPHY_CONDITIONS,
    )
    trophy_icon = models.ForeignKey(
        TrophyIcon,
        on_delete=models.PROTECT,
        related_name="award_set_items",
    )

    class Meta:
        unique_together = (("award_set", "condition"),)

    def __str__(self):
        return f"{self.award_set} - {self.get_condition_display()}"
