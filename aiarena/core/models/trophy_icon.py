import logging

from django.db import models

from .bot import Bot


logger = logging.getLogger(__name__)


class TrophyIcon(models.Model):
    name = models.CharField(max_length=64, unique=True)
    image = models.ImageField(upload_to="trophy_images/")

    def __str__(self):
        return self.name
