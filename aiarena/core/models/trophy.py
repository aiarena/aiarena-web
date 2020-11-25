import logging

from django.db import models

from .bot import Bot
from .trophy_icon import TrophyIcon

logger = logging.getLogger(__name__)


class Trophy(models.Model):
    icon = models.ForeignKey(TrophyIcon, on_delete=models.SET_NULL, blank=True, null=True)
    bot = models.ForeignKey(Bot, on_delete=models.CASCADE)
    name = models.CharField(max_length=64)
