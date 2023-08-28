import logging

from django.db import models


logger = logging.getLogger(__name__)


class Tag(models.Model):
    name = models.CharField(max_length=32, unique=True)

    def __str__(self):
        return self.name
