import logging
from django.db import models

logger = logging.getLogger(__name__)


class CompetitionType(models.TextChoices):
    TOURNAMENT = u'T', 'Tournament'
    LEAGUE = u'L', 'League'
    CUSTOM = u'C', 'Custom'
    flash_challenge = u'F', 'FlashChallenge'


class Competition(models.Model):
    name = models.CharField(max_length=50, unique=True)
    type = models.CharField(max_length=32,
                            choices=CompetitionType.choices,
                            default=CompetitionType.LEAGUE)

    enabled = models.BooleanField(default=False)

    def get_type(self):
        return CompetitionType(self.type).name.title()

    def get_divisions(self):
        return self.divisions.all()

    def __str__(self):
        return f"{self.name}, {self.get_type()}, Divisions: {len(self.get_divisions())}"
