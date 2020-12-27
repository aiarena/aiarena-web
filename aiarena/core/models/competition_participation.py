import logging

from django.db import models
from django.utils.text import slugify

from aiarena.settings import ELO_START_VALUE
from .bot import Bot
from .mixins import LockableModelMixin
from .competition import Competition
from ..storage import OverwriteStorage
from ..validators import validate_not_nan, validate_not_inf

logger = logging.getLogger(__name__)


def elo_graph_upload_to(instance, filename):
    return '/'.join(['graphs', f'{instance.competition_id}_{instance.bot.id}_{instance.bot.name}.png'])


class CompetitionParticipation(models.Model, LockableModelMixin):
    competition = models.ForeignKey(Competition, on_delete=models.CASCADE)
    bot = models.ForeignKey(Bot, on_delete=models.CASCADE, related_name='competition_participations')
    elo = models.SmallIntegerField(default=ELO_START_VALUE)
    match_count = models.IntegerField(default=0)
    win_perc = models.FloatField(blank=True, null=True, validators=[validate_not_nan, validate_not_inf])
    win_count = models.IntegerField(default=0)
    loss_perc = models.FloatField(blank=True, null=True, validators=[validate_not_nan, validate_not_inf])
    loss_count = models.IntegerField(default=0)
    tie_perc = models.FloatField(blank=True, null=True, validators=[validate_not_nan, validate_not_inf])
    tie_count = models.IntegerField(default=0)
    crash_perc = models.FloatField(blank=True, null=True, validators=[validate_not_nan, validate_not_inf])
    crash_count = models.IntegerField(default=0)
    elo_graph = models.FileField(upload_to=elo_graph_upload_to, storage=OverwriteStorage(), blank=True, null=True)
    highest_elo = models.IntegerField(blank=True, null=True)
    slug = models.SlugField(max_length=255)
    active = models.BooleanField(default=True)

    def __str__(self):
        return self.competition.name + ' ' + str(self.bot)

    def save(self, *args, **kwargs):
        self.slug = slugify(f'{self.bot.name} {self.competition.name}')
        super().save(*args, **kwargs)

