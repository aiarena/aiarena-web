import logging

from django.db import models

logger = logging.getLogger(__name__)


class Competition(models.Model):
    TYPES = (
        ('ladder', 'Ladder'),
        ('tournament', 'Tournament'),
        ('flash_challenge', 'Flash Challenge'),
    )
    name = models.CharField(max_length=50, unique=True)
    type = models.CharField(max_length=16, choices=TYPES)
    # enabled = models.BooleanField(default=False)
