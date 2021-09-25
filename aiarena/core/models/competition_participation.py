import logging

from django.core.exceptions import ValidationError
from django.db import models
from django.utils.text import slugify
from django.core.validators import MinValueValidator

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
    competition = models.ForeignKey(Competition, on_delete=models.CASCADE, related_name='participations')
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
    slug = models.SlugField(max_length=255, blank=True)
    active = models.BooleanField(default=True)

    # Tracks the division the player is in in the Competition. 
    # Highest division will be 1 and lowest will be competition.target_n_divisions
    # Only players that haven't been placed into the latest cycle should have division_num=DEFAULT_DIVISION
    MIN_DIVISION = 1
    DEFAULT_DIVISION = 0
    division_num = models.IntegerField(default=DEFAULT_DIVISION, validators=[MinValueValidator(DEFAULT_DIVISION)])
    in_placements = models.BooleanField(default=True)

    def validate_unique(self, exclude=None):
        if self.active:
            bot_limit = self.bot.user.get_active_bots_limit()
            if CompetitionParticipation.objects.exclude(pk=self.pk)\
                    .filter(bot__user=self.bot.user, active=True).count() >= bot_limit:
                raise ValidationError(
                        'Too many active participations already exist for this user.'
                        ' You are allowed ' + str(bot_limit) + ' active participations in competitions.')
        super().validate_unique(exclude=exclude)
        

    def clean(self):
        self.validate_competition_accepting_new_participants()
        super().clean()
        
    def __str__(self):
        return self.competition.name + ' ' + str(self.bot)

    def save(self, *args, **kwargs):
        self.slug = slugify(f'{self.bot.name} {self.competition.name}')
        super().save(*args, **kwargs)

    def validate_competition_accepting_new_participants(self):
        if self.id is None and not self.competition.is_accepting_new_participants:
            raise ValidationError('That competition is not accepting new participants.')


