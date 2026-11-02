import calendar
from datetime import datetime

from django.core.exceptions import ValidationError
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.utils import timezone

from .award_set import AwardSet
from .bot_race import BotRace
from .game_mode import GameMode


class CompetitionSchedule(models.Model):
    """
    Defines an annually recurring competition.

    Start and end dates are specified without years.
    Each year, the scheduler will create new Competition automatically
    using these settings.
    """

    name = models.CharField(
        max_length=50,
        help_text="Supports {year}, e.g. Championship {year}",
    )

    enabled = models.BooleanField(default=True)

    game_mode = models.ForeignKey(
        GameMode,
        on_delete=models.PROTECT,
        related_name="competition_schedules",
    )

    award_set = models.ForeignKey(
        AwardSet,
        on_delete=models.PROTECT,
        blank=True,
        null=True,
    )

    # Annual schedule
    """ Setting a day to 31 - means the last day of the month - regardless of month. 
     Febuary has 28 days normally, but 29 in a leap year. 
     The scheduler will automatically handle this by setting the date to 31 (or in this case 29).
    """
    start_month = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(12)],
    )
    start_day = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(31)],
    )
    start_time = models.TimeField(
        default="00:00",
        help_text="Time the competition opens (UTC).",
    )

    end_month = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(12)],
    )
    end_day = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(31)],
    )
    end_time = models.TimeField(
        default="00:00",
        help_text="Time the competition starts closing (UTC).",
    )

    # Competition configuration
    max_active_rounds = models.IntegerField(default=2)

    target_n_divisions = models.IntegerField(
        default=1,
        validators=[MinValueValidator(1)],
    )

    n_divisions = models.IntegerField(
        default=1,
        validators=[MinValueValidator(1)],
    )

    target_division_size = models.IntegerField(
        default=2,
        validators=[MinValueValidator(2)],
    )

    rounds_per_cycle = models.IntegerField(
        default=1,
        validators=[MinValueValidator(1)],
    )

    n_placements = models.IntegerField(
        default=0,
        validators=[MinValueValidator(0)],
    )

    playable_races = models.ManyToManyField(
        BotRace,
        blank=True,
    )

    require_trusted_infrastructure = models.BooleanField(
        default=True,
    )

    indepth_bot_statistics_enabled = models.BooleanField(
        default=True,
    )

    def __str__(self):
        return self.name

    @staticmethod
    def resolve_date(year, month, day, time):
        """
        Convert a yearless month/day and time into a datetime.

        Days exceeding the number of days in the month
        are clamped to the last valid day.
        """
        last_day = calendar.monthrange(year, month)[1]

        return datetime(
            year=year,
            month=month,
            day=min(day, last_day),
            hour=time.hour,
            minute=time.minute,
            second=time.second,
            tzinfo=timezone.get_default_timezone(),
        )

    def get_start(self, year):
        return self.resolve_date(
            year,
            self.start_month,
            self.start_day,
            self.start_time,
        )

    def get_end(self, year):
        start = self.get_start(year)

        end = self.resolve_date(
            year,
            self.end_month,
            self.end_day,
            self.end_time,
        )

        # Handle competitions crossing into the following year.
        if end <= start:
            end = self.resolve_date(
                year + 1,
                self.end_month,
                self.end_day,
                self.end_time,
            )

        return end

    def get_competition_name(self, year):
        name = self.name.replace("{year}", str(year))

        if len(name) > 50:
            raise ValidationError("Generated competition name exceeds 50 characters.")

        return name

    def clean(self):
        super().clean()

        # All day values 1-31 are supported through clamping.
        # Validate the calendar boundaries after resolution.
        fields = (
            self.start_month,
            self.start_day,
            self.start_time,
            self.end_month,
            self.end_day,
            self.end_time,
        )

        if any(value is None for value in fields):
            return

        try:
            self.get_start(2024)
            self.get_end(2024)
        except (ValueError, OverflowError) as exc:
            raise ValidationError(f"Invalid competition schedule: {exc}")
