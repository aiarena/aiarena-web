import logging

from django.db import models

from .bot import Bot

logger = logging.getLogger(__name__)


class Trophy(models.Model):
    bot = models.ForeignKey(Bot, on_delete=models.CASCADE)
    name = models.TextField()
