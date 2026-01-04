import logging

from django.conf import settings
from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator
from django.db import models
from django.db.models import Prefetch
from django.utils.text import slugify

from constance import config
from private_storage.fields import PrivateFileField

from ..validators import validate_not_inf, validate_not_nan
from .bot import Bot
from .competition import Competition
from .mixins import LockableModelMixin


logger = logging.getLogger(__name__)


class CompetitionParticipationSet(models.QuerySet):
    def calculate_trend(self, competition):
        from . import MatchParticipation

        qs = self.prefetch_related(
            Prefetch(
                "bot__matchparticipation_set",
                queryset=MatchParticipation.objects.filter(
                    elo_change__isnull=False,
                    match__requested_by__isnull=True,
                    match__round__competition=competition,
                ).order_by("-match__started")[: config.ELO_TREND_N_MATCHES],
                to_attr="match_participations",
            )
        )

        result = []
        for participant in qs:
            participant.trend = sum(participation.elo_change for participation in participant.bot.match_participations)
            result.append(participant)

        return result


def elo_graph_upload_to(instance, filename):
    return "/".join(["graphs", f"{instance.competition_id}_{instance.bot.id}_{instance.bot.name}.png"])


def elo_graph_update_plot_upload_to(instance, filename):
    return "/".join(["competitions", "stats", f"{instance.id}_elo_graph_update_plot.png"])


def winrate_vs_duration_graph_upload_to(instance, filename):
    return "/".join(["graphs", f"{instance.competition_id}_{instance.bot.id}_{instance.bot.name}_winrate.png"])


class CompetitionParticipation(models.Model, LockableModelMixin):
    competition = models.ForeignKey(Competition, on_delete=models.CASCADE, related_name="participations")
    bot = models.ForeignKey(Bot, on_delete=models.CASCADE, related_name="competition_participations")
    elo = models.SmallIntegerField(default=settings.ELO_START_VALUE)
    match_count = models.IntegerField(default=0)
    win_perc = models.FloatField(default=0, blank=True, validators=[validate_not_nan, validate_not_inf])
    win_count = models.IntegerField(default=0)
    loss_perc = models.FloatField(default=0, blank=True, validators=[validate_not_nan, validate_not_inf])
    loss_count = models.IntegerField(default=0)
    tie_perc = models.FloatField(default=0, blank=True, validators=[validate_not_nan, validate_not_inf])
    tie_count = models.IntegerField(default=0)
    crash_perc = models.FloatField(default=0, blank=True, validators=[validate_not_nan, validate_not_inf])
    crash_count = models.IntegerField(default=0)
    elo_graph = models.FileField(upload_to=elo_graph_upload_to, blank=True, null=True)
    elo_graph_update_plot = PrivateFileField(upload_to=elo_graph_update_plot_upload_to, blank=True, null=True)
    winrate_vs_duration_graph = models.FileField(upload_to=winrate_vs_duration_graph_upload_to, blank=True, null=True)
    highest_elo = models.IntegerField(blank=True, null=True)
    slug = models.SlugField(max_length=255, blank=True)
    active = models.BooleanField(default=True)
    participated_in_most_recent_round = models.BooleanField(default=False)

    # Tracks the division the player is in in the Competition.
    # Highest division will be 1 and lowest will be competition.target_n_divisions
    # Only players that haven't been placed into the latest cycle should have division_num=DEFAULT_DIVISION
    MIN_DIVISION = 1
    DEFAULT_DIVISION = 0
    division_num = models.IntegerField(default=DEFAULT_DIVISION, validators=[MinValueValidator(DEFAULT_DIVISION)])
    in_placements = models.BooleanField(default=True)

    objects = CompetitionParticipationSet.as_manager()

    class Meta:
        unique_together = ("competition", "bot")

    def validate_unique(self, exclude=None):
        if self.active:
            from ..services import supporters  # avoid circular import

            bot_limit = supporters.get_active_bots_limit(self.bot.user)
            if (
                CompetitionParticipation.objects.exclude(pk=self.pk)
                .filter(bot__user=self.bot.user, active=True)
                .count()
                >= bot_limit
            ):
                raise ValidationError(
                    "Too many active participations already exist for this user."
                    " You are allowed " + str(bot_limit) + " active participations in competitions."
                )
        super().validate_unique(exclude=exclude)

    def clean(self):
        self.validate_competition_accepting_new_participants()
        self.validate_race_restrictions()
        super().clean()

    def __str__(self):
        return self.competition.name + " " + str(self.bot)

    def save(self, *args, **kwargs):
        self.slug = slugify(f"{self.bot.name} {self.competition.name}")
        super().save(*args, **kwargs)

    def validate_competition_accepting_new_participants(self):
        if self.id is None and not self.competition.is_accepting_new_participants:
            raise ValidationError("That competition is not accepting new participants.")

    def validate_race_restrictions(self):
        if self.competition.playable_races.count() != 0 and not self.bot_race_is_permitted(self.bot.plays_race):
            allowed_races_string = " ".join(
                [race.get_label_display() for race in self.competition.playable_races.all()]
            )
            raise ValidationError(f"This competition is restricted to the following bot races: {allowed_races_string}")

    def bot_race_is_permitted(self, bot_race):
        return self.competition.playable_races.filter(id=bot_race.id).exists()
