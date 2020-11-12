import logging
from django.db import models
from django.urls import reverse
from django.utils.functional import cached_property
from django.utils.html import escape
from django.utils.safestring import mark_safe

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

    def map_pool(self):
        return self.maps.all()

    @property
    def get_divisions(self):
        return self.divisions.all()

    @cached_property
    def get_absolute_url(self):
        return reverse('competition', kwargs={'pk': self.pk})

    @cached_property
    def as_html_link(self):
        return mark_safe(f'<a href="{self.get_absolute_url}">{escape(self.__str__())}</a>')

    def __str__(self):
        return f"{self.name}, {self.get_type()}, Divisions: {len(self.get_divisions)}"
