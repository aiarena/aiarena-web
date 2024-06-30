import logging
import time

from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models
from django.utils.functional import cached_property

from ..utils import Elo
from .bot import Bot
from .match import Match
from .mixins import LockableModelMixin
from .user import User


logger = logging.getLogger(__name__)
ELO = Elo(settings.ELO_K)

# todo: move sanity checking to DB constraints:
# https://docs.djangoproject.com/en/3.0/ref/models/options/#constraints
# Requires upgrade to django 2.2


def replay_file_upload_to(instance, filename):
    match = (
        Match.objects.only("map__name", "id")
        .prefetch_related("matchparticipation_set", "matchparticipation_set__bot")
        .select_related("map")
        .get(id=instance.match.id)
    )
    return "/".join(
        [
            "replays",
            f"{match.id}"
            f"_{match.matchparticipation_set.get(participant_number=1).bot.name}"
            f"_{match.matchparticipation_set.get(participant_number=2).bot.name}"
            f"_{match.map.name}.SC2Replay",
        ]
    )


def arenaclient_log_upload_to(instance, filename):
    return "/".join(["arenaclient-logs", f"{instance.match.id}_arenaclientlog.zip"])


class Result(models.Model, LockableModelMixin):
    TYPES = (
        ("MatchCancelled", "MatchCancelled"),
        ("InitializationError", "InitializationError"),
        ("Error", "Error"),
        ("Player1Win", "Player1Win"),
        ("Player1Crash", "Player1Crash"),
        ("Player1TimeOut", "Player1TimeOut"),
        ("Player1RaceMismatch", "Player1RaceMismatch"),
        ("Player1Surrender", "Player1Surrender"),
        ("Player2Win", "Player2Win"),
        ("Player2Crash", "Player2Crash"),
        ("Player2TimeOut", "Player2TimeOut"),
        ("Player2RaceMismatch", "Player2RaceMismatch"),
        ("Player2Surrender", "Player2Surrender"),
        ("Tie", "Tie"),
    )
    winner = models.ForeignKey(Bot, on_delete=models.PROTECT, related_name="matches_won", blank=True, null=True)
    type = models.CharField(max_length=32, choices=TYPES, db_index=True)
    created = models.DateTimeField(auto_now_add=True, db_index=True)
    replay_file = models.FileField(upload_to=replay_file_upload_to, blank=True, null=True)
    game_steps = models.IntegerField(db_index=True)
    submitted_by = models.ForeignKey(
        User, on_delete=models.PROTECT, blank=True, null=True, related_name="submitted_results"
    )
    arenaclient_log = models.FileField(upload_to=arenaclient_log_upload_to, blank=True, null=True)
    interest_rating = models.FloatField(blank=True, null=True, db_index=True)
    date_interest_rating_calculated = models.DateTimeField(blank=True, null=True)
    replay_file_has_been_cleaned = models.BooleanField(default=False)
    """This is set to true when the replay file is deleted by the cleanup job."""
    arenaclient_log_has_been_cleaned = models.BooleanField(default=False)
    """This is set to true when the arena log file is deleted by the cleanup job."""

    def __str__(self):
        return self.created.__str__() + " " + str(self.type) + " " + str(self.duration_seconds)

    @cached_property
    def duration_seconds(self):
        return (self.created - self.match.started).total_seconds()

    @cached_property
    def game_time_formatted(self):
        return time.strftime("%H:%M:%S", time.gmtime(self.game_steps / 22.4))

    @cached_property
    def participant1(self):
        return self.match.participant1

    @cached_property
    def participant2(self):
        return self.match.participant2

    def validate_replay_file_requirement(self):
        if (self.has_winner or self.is_tie) and not self.replay_file and not self.replay_file_has_been_cleaned:
            logger.warning(f"Result for match {self.match.id} failed validation due to a missing replay file.")
            raise ValidationError("A win/loss or tie result must be accompanied by a replay file.")

    def clean(self, *args, **kwargs):
        self.validate_replay_file_requirement()
        super().clean(*args, **kwargs)

    @cached_property
    def has_winner(self):
        return self.type in (
            "Player1Win",
            "Player1Crash",
            "Player1TimeOut",
            "Player1Surrender",
            "Player2Win",
            "Player2Crash",
            "Player2TimeOut",
            "Player2Surrender",
        )

    @cached_property
    def winner_participant_number(self):
        if self.type in ("Player1Win", "Player2Crash", "Player2TimeOut", "Player2Surrender"):
            return 1
        elif self.type in ("Player1Crash", "Player1TimeOut", "Player1Surrender", "Player2Win"):
            return 2
        else:
            return 0

    @cached_property
    def is_tie(self):
        return self.type == "Tie"

    @cached_property
    def is_timeout(self):
        return self.type == "Player1TimeOut" or self.type == "Player2TimeOut"

    @cached_property
    def is_crash(self):
        return self.type == "Player1Crash" or self.type == "Player2Crash"

    @cached_property
    def is_init_error(self):
        return self.type == "InitializationError"

    @cached_property
    def is_crash_or_timeout(self):
        return self.is_crash or self.is_timeout

    @cached_property
    def is_crash_or_timeout_or_init_error(self):
        return self.is_crash_or_timeout or self.is_init_error

    @cached_property
    def get_causing_participant_of_crash_or_timeout_result(self):
        if self.type == "Player1TimeOut" or self.type == "Player1Crash":
            return self.participant1
        elif self.type == "Player2TimeOut" or self.type == "Player2Crash":
            return self.participant2
        else:
            return None

    @cached_property
    def get_winner_loser_competition_participants(self):
        bot1, bot2 = self.get_competition_participants
        if self.type in ("Player1Win", "Player2Crash", "Player2TimeOut", "Player2Surrender"):
            return bot1, bot2
        elif self.type in ("Player2Win", "Player1Crash", "Player1TimeOut", "Player1Surrender"):
            return bot2, bot1
        else:
            raise Exception("There was no winner or loser for this match.")

    @cached_property
    def get_winner_loser_bots(self):
        bot1, bot2 = self.get_match_participant_bots
        if self.type in ("Player1Win", "Player2Crash", "Player2TimeOut", "Player2Surrender"):
            return bot1, bot2
        elif self.type in ("Player2Win", "Player1Crash", "Player1TimeOut", "Player1Surrender"):
            return bot2, bot1
        else:
            raise Exception("There was no winner or loser for this match.")

    @cached_property
    def get_competition_participants(self):
        """Returns the SeasonParticipant models for the MatchParticipants"""
        from .match_participation import MatchParticipation

        match_id = self.match.id
        first = MatchParticipation.objects.get(match_id=match_id, participant_number=1)
        second = MatchParticipation.objects.get(match_id=match_id, participant_number=2)
        return first.competition_participant, second.competition_participant

    @cached_property
    def get_match_participants(self):
        from .match_participation import MatchParticipation

        first = MatchParticipation.objects.get(match=self.match, participant_number=1)
        second = MatchParticipation.objects.get(match=self.match, participant_number=2)
        return first, second

    @cached_property
    def get_match_participant_bots(self):
        first, second = self.get_match_participants
        return first.bot, second.bot

    def clean_replay_file(self) -> bool:
        if self.replay_file:
            self.replay_file_has_been_cleaned = True
            self.replay_file.delete()
            return True
        return False

    def clean_arenaclient_log(self) -> bool:
        if self.arenaclient_log:
            self.arenaclient_log_has_been_cleaned = True
            self.arenaclient_log.delete()
            return True
        return False

    def save(self, *args, **kwargs):
        from .match_participation import MatchParticipation

        # set winner
        if self.has_winner:
            self.winner = (
                MatchParticipation.objects.select_related("bot")
                .get(match=self.match, participant_number=self.winner_participant_number)
                .bot
            )

        self.full_clean()  # ensure validation is run on save
        super().save(*args, **kwargs)

    def adjust_elo(self):
        if self.has_winner:
            sp_winner, sp_loser = self.get_winner_loser_competition_participants
            self._apply_elo_delta(ELO.calculate_elo_delta(sp_winner.elo, sp_loser.elo, 1.0), sp_winner, sp_loser)
        elif self.type == "Tie":
            sp_first, sp_second = self.get_competition_participants
            self._apply_elo_delta(ELO.calculate_elo_delta(sp_first.elo, sp_second.elo, 0.5), sp_first, sp_second)

    @cached_property
    def get_initial_elos(self):
        first, second = self.get_competition_participants
        return first.elo, second.elo

    def _apply_elo_delta(self, delta, sp1, sp2):
        delta = int(round(delta))
        sp1.elo += delta
        sp1.save()
        sp2.elo -= delta
        sp2.save()
