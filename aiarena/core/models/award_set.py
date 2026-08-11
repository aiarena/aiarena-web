# award_set.py

import logging

from django.db import models


logger = logging.getLogger(__name__)


class AwardSet(models.Model):
    """A grouping of rewards. Attatch to a competition to enable award features like checking and awarding trophies."""

    name = models.CharField(max_length=64, unique=True)

    def __str__(self):
        return self.name
