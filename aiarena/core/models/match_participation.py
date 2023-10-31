from django.core.exceptions import ObjectDoesNotExist
from django.db import models
from django.utils.functional import cached_property

from private_storage.fields import PrivateFileField

from aiarena.core.validators import validate_not_inf, validate_not_nan

from .bot import Bot
from .match import Match
from .mixins import LockableModelMixin


def match_log_upload_to(instance, filename):
    return "/".join(["match-logs", str(instance.id)])


class MatchParticipation(models.Model, LockableModelMixin):
    RESULT_TYPES = (
        ("none", "None"),
        ("win", "Win"),
        ("loss", "Loss"),
        ("tie", "Tie"),
    )
    CAUSE_TYPES = (
        ("game_rules", "Game Rules"),  # This represents the game handing out a result
        ("crash", "Crash"),  # A bot crashed
        ("timeout", "Timeout"),  # A bot timed out
        ("race_mismatch", "Race Mismatch"),  # A bot joined the match with the wrong race
        ("match_cancelled", "Match Cancelled"),  # The match was cancelled
        ("initialization_failure", "Initialization Failure"),  # A bot failed to initialize
        ("error", "Error"),
        # There was an unspecified error running the match (this should only be paired with a 'none' result)
    )
    match = models.ForeignKey(Match, on_delete=models.CASCADE)
    participant_number = models.PositiveSmallIntegerField(db_index=True)
    bot = models.ForeignKey(Bot, on_delete=models.PROTECT)
    resultant_elo = models.SmallIntegerField(null=True)
    """The bot's ELO as a result of this match.
    Note that this isn't necessarily the same as starting_elo + elo_change."""
    elo_change = models.SmallIntegerField(null=True)
    """The amount the bot's ELO changed as a result of this match."""
    match_log = PrivateFileField(upload_to=match_log_upload_to, blank=True, null=True)
    avg_step_time = models.FloatField(blank=True, null=True, validators=[validate_not_nan, validate_not_inf])
    result = models.CharField(max_length=32, choices=RESULT_TYPES, blank=True, null=True)
    result_cause = models.CharField(max_length=32, choices=CAUSE_TYPES, blank=True, null=True)
    use_bot_data = models.BooleanField(default=True)
    """Whether arena clients should download this bot's data for the match. 
    If this is False, update_bot_data is also assumed False"""
    update_bot_data = models.BooleanField(default=True)
    """Whether to update this bot's data after the match."""
    match_log_has_been_cleaned = models.BooleanField(default=True)
    """This is set to true when the match log file is deleted by the cleanup job."""

    def __str__(self):
        return self.bot.name

    @property
    def starting_elo(self):
        if self.resultant_elo is None or self.elo_change is None:
            raise Exception("Cannot calculate starting ELO when resultant ELO or ELO change is None!")
        return (
            self.resultant_elo - self.elo_change
            if self.resultant_elo is not None and self.elo_change is not None
            else None
        )

    @property
    def step_time_ms(self):
        return (self.avg_step_time if self.avg_step_time is not None else 0) * 1000

    @property
    def crashed(self):
        return self.result == "loss" and self.result_cause in ["crash", "timeout", "initialization_failure"]

    @property
    def triggered_a_crash_limit_alert(self):
        try:
            self.botcrashlimitalert  # force load from database
            return True
        except ObjectDoesNotExist:
            return False

    @cached_property
    def competition_participant(self):
        obj = self.__class__.objects.select_related("match", "match__round", "match__round__competition").get(
            id=self.id
        )
        return obj.match.round.competition.participations.get(bot_id=self.bot_id)

    @cached_property
    def allow_parallel_run(self):
        """Whether this bot can participate in this match when already in other non-parallel matches."""
        data_dict = self.__class__.objects.values("use_bot_data", "update_bot_data").get(id=self.id)
        return not data_dict["use_bot_data"] or not data_dict["update_bot_data"]

    @cached_property
    def available_to_start_match(self):
        """Whether this bot can start the match at this time."""
        if not self.allow_parallel_run:
            # Get all the matches that contain this bot that have started and not finished
            # Then check to see if they should block entry into a new match
            matches = Match.objects.only("id").filter(
                matchparticipation__bot_id=self.bot_id, started__isnull=False, result__isnull=True
            )
            for match in matches:
                for p in match.matchparticipation_set.filter(bot_id=self.bot_id):
                    if not p.allow_parallel_run:
                        return False
        return True

    def calculate_relative_result(self, result_type):
        if result_type in ["MatchCancelled", "InitializationError", "Error"]:
            return "none"
        elif result_type in ["Player1Win", "Player2Crash", "Player2TimeOut", "Player2RaceMismatch", "Player2Surrender"]:
            return "win" if self.participant_number == 1 else "loss"
        elif result_type in ["Player2Win", "Player1Crash", "Player1TimeOut", "Player1RaceMismatch", "Player1Surrender"]:
            return "win" if self.participant_number == 2 else "loss"
        elif result_type == "Tie":
            return "tie"
        else:
            raise Exception("Unrecognized result type!")

    @staticmethod
    def calculate_result_cause(result_type):
        if result_type in ["Player1Win", "Player2Win", "Tie", "Player1Surrender", "Player2Surrender"]:
            return "game_rules"
        elif result_type in ["Player1Crash", "Player2Crash"]:
            return "crash"
        elif result_type in ["Player1TimeOut", "Player2TimeOut"]:
            return "timeout"
        elif result_type in ["Player1RaceMismatch", "Player2RaceMismatch"]:
            return "race_mismatch"
        elif result_type == "MatchCancelled":
            return "match_cancelled"
        elif result_type == "InitializationError":
            return "initialization_failure"
        elif result_type == "Error":
            return "error"
        else:
            raise Exception("Unrecognized result type!")

    def can_download_match_log(self, user):
        return self.bot.user == user or user.is_staff
