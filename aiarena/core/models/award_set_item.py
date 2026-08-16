# award_set_item.py

import logging

from django.db import models

from .award_set import AwardSet
from .trophy import TrophyCondition
from .trophy_icon import TrophyIcon


logger = logging.getLogger(__name__)


class AwardSetItem(models.Model):
    """An item in an award_set. It corresponds of a reward (trophy icon) mapped to a condition - such as first place, top 10, coolest hat, best zerg, etc.
    It is not in itself a reward - but rather an item that can be used to check if an award should be administered.
    """

    award_set = models.ForeignKey(
        AwardSet,
        on_delete=models.CASCADE,
        related_name="items",
    )
    condition = models.CharField(
        max_length=32,
        choices=TrophyCondition.choices,
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
