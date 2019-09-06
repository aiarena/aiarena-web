import logging
import uuid
from enum import Enum

from constance import config
from django.contrib.auth.models import AbstractUser
from django.core.exceptions import ValidationError
from django.db import models, transaction, connection
from django.db.models import F
from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from django.urls import reverse
from django.utils import timezone
from django.utils.html import escape
from private_storage.fields import PrivateFileField

from aiarena import settings
from aiarena.api.arenaclient.exceptions import NotEnoughAvailableBots, NoMaps, NotEnoughActiveBots, MaxActiveRounds
from aiarena.core.exceptions import BotNotInMatchException, BotAlreadyInMatchException
from aiarena.core.storage import OverwritePrivateStorage, OverwriteStorage
from aiarena.core.utils import calculate_md5_django_filefield
from aiarena.core.validators import validate_not_nan, validate_not_inf
from aiarena.settings import ELO_START_VALUE, ELO, BOT_ZIP_MAX_SIZE

logger = logging.getLogger(__name__)


class Map(models.Model):
    name = models.CharField(max_length=50, unique=True)
    file = models.FileField(upload_to='maps')

    def __str__(self):
        return self.name

    @staticmethod
    def random():
        # todo: apparently this is really slow
        # https://stackoverflow.com/questions/962619/how-to-pull-a-random-record-using-djangos-orm#answer-962672
        return Map.objects.order_by('?').first()


class User(AbstractUser):
    email = models.EmailField(unique=True)
    service_account = models.BooleanField(default=False)

    def get_absolute_url(self):
        return reverse('author', kwargs={'pk': self.pk})

    def as_html_link(self):
        return '<a href="{0}">{1}</a>'.format(self.get_absolute_url(), escape(self.__str__()))


class Round(models.Model):
    started = models.DateTimeField(auto_now_add=True)
    finished = models.DateTimeField(blank=True, null=True)
    complete = models.BooleanField(default=False)

    # if all the matches have been run, mark this as complete
    def update_if_completed(self):
        # if there are no matches without results, this round is complete
        if Match.objects.filter(round=self, result__isnull=True).count() == 0:
            self.complete = True
            self.finished = timezone.now()
            self.save()

    @staticmethod
    def max_active_rounds_reached():
        return Round.objects.filter(complete=False).count() >= config.MAX_ACTIVE_ROUNDS


# todo: structure for separate ladder types
class Match(models.Model):
    map = models.ForeignKey(Map, on_delete=models.PROTECT)
    created = models.DateTimeField(auto_now_add=True)
    started = models.DateTimeField(blank=True, null=True, editable=False)
    assigned_to = models.ForeignKey(User, on_delete=models.PROTECT, blank=True, null=True)
    round = models.ForeignKey(Round, on_delete=models.CASCADE, blank=True, null=True)

    def __str__(self):
        return self.id.__str__()

    class StartResult(Enum):
        SUCCESS = 1
        BOT_ALREADY_IN_MATCH = 2
        FAIL_ALREADY_STARTED = 3

    def start(self, assign_to):
        with transaction.atomic():
            Match.objects.select_for_update().get(id=self.id)  # lock self to avoid race conditions
            if self.started is None:
                # is a bot currently in a match?
                participants = Participant.objects.select_for_update().filter(match=self)
                for p in participants:
                    if p.bot.in_match:
                        return Match.StartResult.BOT_ALREADY_IN_MATCH

                for p in participants:
                    p.bot.enter_match(self)

                self.started = timezone.now()
                self.assigned_to = assign_to
                self.save()
                return Match.StartResult.SUCCESS
            else:
                return Match.StartResult.FAIL_ALREADY_STARTED

    def get_participant1(self):
        return Participant.objects.get(match=self, participant_number=1)

    def get_participant2(self):
        return Participant.objects.get(match=self, participant_number=2)

    @staticmethod
    def _queue_round_robin_matches_for_all_active_bots():
        if Map.objects.count() == 0:
            raise NoMaps()
        if Bot.objects.filter(active=True).count() <= 1:  # need at least 2 active bots for a match
            raise NotEnoughActiveBots()

        round = Round.objects.create()

        active_bots = Bot.objects.filter(active=True)
        already_processed_bots = []

        # loop through and generate matches for all active bots
        for bot1 in active_bots:
            already_processed_bots.append(bot1.id)
            for bot2 in Bot.objects.filter(active=True).exclude(id__in=already_processed_bots):
                Match.create(round, Map.random(), bot1, bot2)

    @staticmethod
    def start_next_match(requesting_user):

        Bot.timeout_overtime_bot_games()

        with connection.cursor() as cursor:
            # Lock the matches table
            # this needs to happen so that if we end up having to generate a new set of matches
            # then we don't hit a race condition
            # MySql also requires we lock any other tables we access as well.
            cursor.execute(
                "LOCK TABLES {0} WRITE, {1} WRITE, {2} WRITE, {3} WRITE, {4} READ".format(Match._meta.db_table,
                                                                                          Round._meta.db_table,
                                                                                          Participant._meta.db_table,
                                                                                          Bot._meta.db_table,
                                                                                          Map._meta.db_table))
            try:
                match = Match._locate_and_return_started_match(requesting_user)
                if match is None:
                    if Bot.objects.filter(active=True, in_match=False).count() < 2:
                        # All the active bots are already in a match
                        # ROLLBACK here so the UNLOCK statement doesn't commit changes
                        cursor.execute("ROLLBACK")
                        raise NotEnoughAvailableBots()
                    elif Round.max_active_rounds_reached():
                        # ROLLBACK here so the UNLOCK statement doesn't commit changes
                        cursor.execute("ROLLBACK")
                        raise MaxActiveRounds()
                    else:  # generate new round
                        Match._queue_round_robin_matches_for_all_active_bots()
                        match = Match._locate_and_return_started_match(requesting_user)
                        if match is None:
                            cursor.execute("ROLLBACK")
                            raise Exception("Failed to start match for unknown reason.")
                        else:
                            return match
                else:
                    return match

            finally:
                # pass
                cursor.execute("UNLOCK TABLES;")

    @staticmethod
    def create(round, map, bot1, bot2):
        match = Match.objects.create(map=map, round=round)
        # create match participants
        Participant.objects.create(match=match, participant_number=1, bot=bot1)
        Participant.objects.create(match=match, participant_number=2, bot=bot2)
        return match

    # todo: let us specify the map
    @staticmethod
    def request_bot_match(bot, opponent=None):
        return Match.create(None, Map.random(), bot,
                            opponent if opponent is not None else bot.get_random_available_excluding_self())

    class CancelResult(Enum):
        SUCCESS = 1
        MATCH_DOES_NOT_EXIST = 3
        RESULT_ALREADY_EXISTS = 2

    def cancel(self, requesting_user):
        with transaction.atomic():
            try:
                # do this to lock the record
                # select_related() for the round data
                match = Match.objects.select_related('round').select_for_update().get(pk=self.id)
            except Match.DoesNotExist:
                return Match.CancelResult.MATCH_DOES_NOT_EXIST  # should basically not happen, but just in case

            if Result.objects.filter(match=match).count() > 0:
                return Match.CancelResult.RESULT_ALREADY_EXISTS

            Result.objects.create(match=match, type='MatchCancelled', game_steps=0, submitted_by=requesting_user)

            # attempt to kick the bots from the match
            if match.started:
                try:
                    bot1 = match.participant_set.select_related().select_for_update().get(participant_number=1).bot
                    bot1.leave_match(match.id)
                except BotNotInMatchException:
                    pass
                try:
                    bot2 = match.participant_set.select_related().select_for_update().get(participant_number=2).bot
                    bot2.leave_match(match.id)
                except BotNotInMatchException:
                    pass
            else:
                match.started = timezone.now()
                match.save()

            if match.round is not None:
                match.round.update_if_completed()

    @classmethod
    def _locate_and_return_started_match(cls, requesting_user):
        # todo: apparently order_by('?') is really slow
        # https://stackoverflow.com/questions/962619/how-to-pull-a-random-record-using-djangos-orm#answer-962672
        # Wrapping the model call here in list() fixes the ordering not being applied.
        # Probably due to Django's lazy evaluation - it forces evaluation thus ensuring the order by is processed
        for match in list(
                Match.objects.filter(started__isnull=True).order_by(F('round_id').asc(nulls_last=False), '?')):
            if match.start(requesting_user) == Match.StartResult.SUCCESS:
                return match
        return None

    def get_absolute_url(self):
        return reverse('match', kwargs={'pk': self.pk})

    def as_html_link(self):
        return '<a href="{0}">{1}</a>'.format(self.get_absolute_url(), escape(self.__str__()))


def bot_zip_upload_to(instance, filename):
    return '/'.join(['bots', str(instance.id), 'bot_zip'])


def bot_data_upload_to(instance, filename):
    return '/'.join(['bots', str(instance.id), 'bot_data'])


class Bot(models.Model):
    RACES = (
        ('T', 'Terran'),
        ('Z', 'Zerg'),
        ('P', 'Protoss'),
        ('R', 'Random'),
    )
    TYPES = (
        ('cppwin32', 'cppwin32'),
        ('cpplinux', 'cpplinux'),
        ('dotnetcore', 'dotnetcore'),
        ('java', 'java'),
        ('nodejs', 'nodejs'),
        ('python', 'python'),
    )
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='bots')
    name = models.CharField(max_length=50, unique=True)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    active = models.BooleanField(default=False)  # todo: change this to instead be an enrollment in a ladder?
    in_match = models.BooleanField(default=False)  # todo: move to ladder participant when multiple ladders comes in
    current_match = models.ForeignKey(Match, on_delete=models.PROTECT, blank=True, null=True,
                                      related_name='bots_currently_in_match')
    elo = models.SmallIntegerField(default=ELO_START_VALUE)
    bot_zip = PrivateFileField(upload_to=bot_zip_upload_to, storage=OverwritePrivateStorage(base_url='/'),
                               max_file_size=BOT_ZIP_MAX_SIZE)
    bot_zip_md5hash = models.CharField(max_length=32, editable=False)
    bot_zip_publicly_downloadable = models.BooleanField(default=False)
    # todo: set a file size limit which will be checked on result submission
    # and the bot deactivated if the file size exceeds it
    bot_data = PrivateFileField(upload_to=bot_data_upload_to, storage=OverwritePrivateStorage(base_url='/'),
                                blank=True, null=True)
    bot_data_md5hash = models.CharField(max_length=32, editable=False, null=True)
    bot_data_publicly_downloadable = models.BooleanField(default=False)
    plays_race = models.CharField(max_length=1, choices=RACES)
    type = models.CharField(max_length=32, choices=TYPES)
    # the ID displayed to other bots during a game so they can recognize their opponent
    game_display_id = models.UUIDField(default=uuid.uuid4)

    # todo: once multiple ladders comes in, this will need to be updated to 1 bot race per ladder per user.
    def validate_active_bot_race_per_user(self):
        # if there is already an active bot for this user playing the same race, and this bot is also marked as active
        # then back out
        if Bot.objects.filter(user=self.user, active=True, plays_race=self.plays_race).exclude(
                id=self.id).count() >= config.MAX_USER_BOT_COUNT_ACTIVE_PER_RACE \
                and self.active:
            raise ValidationError(
                'Too many active bots playing that race already exist for this user.'
                ' Each user can only have ' + str(config.MAX_USER_BOT_COUNT_ACTIVE_PER_RACE) + ' active bot(s) per race.')

    def validate_max_bot_count(self):
        if Bot.objects.filter(user=self.user).exclude(id=self.id).count() >= config.MAX_USER_BOT_COUNT:
            raise ValidationError(
                'Maximum bot count of {0} already reached. No more bots may be added for this user.'.format(
                    config.MAX_USER_BOT_COUNT))

    def clean(self):
        self.validate_max_bot_count()
        self.validate_active_bot_race_per_user()

    def __str__(self):
        return self.name

    def enter_match(self, match):
        if not self.in_match:
            self.current_match = match
            self.in_match = True
            self.save()
        else:
            raise BotAlreadyInMatchException('Cannot enter a match - bot is already in one.')

    def leave_match(self, match_id=None):
        if self.in_match and (match_id is None or self.current_match_id == match_id):
            self.current_match = None
            self.in_match = False
            self.save()
        else:
            if match_id is None:
                raise BotNotInMatchException('Cannot leave match - bot is not in one.')
            else:
                raise BotNotInMatchException('Cannot leave match - bot is not in match "{0}".'.format(match_id))

    def bot_data_is_currently_frozen(self):
        # dont alter bot_data while a bot is in a match, unless there was no bot_data initially
        return self.in_match and self.bot_data

    # todo: have arena client check in with web service inorder to delay this
    @staticmethod
    def timeout_overtime_bot_games():
        with transaction.atomic():
            bots_in_matches = Bot.objects.select_for_update().filter(in_match=True,
                                                                     current_match__started__lt=timezone.now() - config.TIMEOUT_MATCHES_AFTER)
            for bot in bots_in_matches:
                logger.warning('bot {0} forcefully removed from match {1}'.format(bot.id, bot.current_match_id))
                bot.leave_match()

            matches_without_result = Match.objects.select_related('round').select_for_update().filter(
                started__lt=timezone.now() - config.TIMEOUT_MATCHES_AFTER, result__isnull=True)
            for match in matches_without_result:
                Result.objects.create(match=match, type='MatchCancelled', game_steps=0)
                if match.round is not None:  # if the match is part of a round, check for round completion
                    match.round.update_if_completed()

    @staticmethod
    def get_random_available():
        # todo: apparently this is really slow
        # https://stackoverflow.com/questions/962619/how-to-pull-a-random-record-using-djangos-orm#answer-962672
        return Bot.objects.filter(active=True, in_match=False).order_by('?').first()

    @staticmethod
    def active_count():
        return Bot.objects.filter(active=True).count()

    @staticmethod
    def get_active():
        return Bot.objects.filter(active=True)

    def get_random_available_excluding_self(self):
        if Bot.active_count() <= 1:
            raise RuntimeError("I am the only bot.")
        return Bot.objects.filter(active=True, in_match=False).exclude(id=self.id).order_by('?').first()

    def get_absolute_url(self):
        return reverse('bot', kwargs={'pk': self.pk})

    def as_html_link(self):
        return '<a href="{0}">{1}</a>'.format(self.get_absolute_url(), escape(self.__str__()))


_UNSAVED_BOT_ZIP_FILEFIELD = 'unsaved_bot_zip_filefield'
_UNSAVED_BOT_DATA_FILEFIELD = 'unsaved_bot_data_filefield'


# The following methods will temporarily store the bot_zip and bot_data files while we wait for the Bot model to be
# saved in order to generate an ID, which can then be used in the path for the bot_zip name
# This needs to happen because we want to use the model ID in the file path, but until the model is saved, it doesn't
# have an ID.
@receiver(pre_save, sender=Bot)
def skip_saving_bot_files(sender, instance, **kwargs):
    # If the Bot model hasn't been created yet (i.e. it's missing its ID) then set any files aside for the time being
    if not instance.pk and not hasattr(instance, _UNSAVED_BOT_ZIP_FILEFIELD):
        setattr(instance, _UNSAVED_BOT_ZIP_FILEFIELD, instance.bot_zip)
        instance.bot_zip = None

    # bot data
    if not instance.pk and not hasattr(instance, _UNSAVED_BOT_DATA_FILEFIELD) and instance.bot_data:
        setattr(instance, _UNSAVED_BOT_DATA_FILEFIELD, instance.bot_data)
        instance.bot_data = None


# todo: currently this doesn't wipe the bot_data hash if the data file is being cleared. Ideally it should.
@receiver(post_save, sender=Bot)
def save_bot_files(sender, instance, created, **kwargs):
    # bot zip
    if created and hasattr(instance, _UNSAVED_BOT_ZIP_FILEFIELD):
        instance.bot_zip = getattr(instance, _UNSAVED_BOT_ZIP_FILEFIELD)
        post_save.disconnect(save_bot_files, sender=sender)
        instance.save()
        post_save.connect(save_bot_files, sender=sender)
        # delete the saved instance
        instance.__dict__.pop(_UNSAVED_BOT_ZIP_FILEFIELD)

    # bot data
    if created and hasattr(instance, _UNSAVED_BOT_DATA_FILEFIELD):
        instance.bot_data = getattr(instance, _UNSAVED_BOT_DATA_FILEFIELD)
        post_save.disconnect(save_bot_files, sender=sender)
        instance.save()
        post_save.connect(save_bot_files, sender=sender)
        # delete the saved instance
        instance.__dict__.pop(_UNSAVED_BOT_DATA_FILEFIELD)

    # Re-calculate the file hashes if required.
    if instance.bot_zip:
        bot_zip_hash = calculate_md5_django_filefield(instance.bot_zip)
        if instance.bot_zip_md5hash != bot_zip_hash:
            instance.bot_zip_md5hash = bot_zip_hash
            post_save.disconnect(save_bot_files, sender=sender)
            instance.save()
            post_save.connect(save_bot_files, sender=sender)

    if instance.bot_data:
        bot_data_hash = calculate_md5_django_filefield(instance.bot_data)
        if instance.bot_data_md5hash != bot_data_hash:
            instance.bot_data_md5hash = bot_data_hash
            post_save.disconnect(save_bot_files, sender=sender)
            instance.save()
            post_save.connect(save_bot_files, sender=sender)


def match_log_upload_to(instance, filename):
    return '/'.join(['match-logs', str(instance.id)])


class Participant(models.Model):
    match = models.ForeignKey(Match, on_delete=models.CASCADE)
    participant_number = models.PositiveSmallIntegerField()
    bot = models.ForeignKey(Bot, on_delete=models.PROTECT, related_name='match_participations')
    resultant_elo = models.SmallIntegerField(null=True)
    elo_change = models.SmallIntegerField(null=True)
    match_log = PrivateFileField(upload_to=match_log_upload_to, storage=OverwritePrivateStorage(base_url='/'),
                                 blank=True, null=True)
    avg_step_time = models.FloatField(blank=True, null=True, validators=[validate_not_nan, validate_not_inf])

    def update_resultant_elo(self):
        self.resultant_elo = self.bot.elo
        self.save()

    def __str__(self):
        return self.bot.name


def arenaclient_log_upload_to(instance, filename):
    return '/'.join(['arenaclient-logs', '{0}_arenaclientlog.zip'.format(instance.match_id)])


class Result(models.Model):
    TYPES = (
        ('MatchCancelled', 'MatchCancelled'),
        ('InitializationError', 'InitializationError'),
        ('Timeout', 'Timeout'),
        ('ProcessingReplay', 'ProcessingReplay'),
        ('Player1Win', 'Player1Win'),
        ('Player1Crash', 'Player1Crash'),
        ('Player1TimeOut', 'Player1TimeOut'),
        ('Player1RaceMismatch', 'Player1RaceMismatch'),
        ('Player2Win', 'Player2Win'),
        ('Player2Crash', 'Player2Crash'),
        ('Player2TimeOut', 'Player2TimeOut'),
        ('Player2RaceMismatch', 'Player2RaceMismatch'),
        ('Tie', 'Tie'),
        ('Error', 'Error'),
    )
    match = models.OneToOneField(Match, on_delete=models.CASCADE, related_name='result')
    winner = models.ForeignKey(Bot, on_delete=models.PROTECT, related_name='matches_won', blank=True, null=True)
    type = models.CharField(max_length=32, choices=TYPES)
    created = models.DateTimeField(auto_now_add=True)
    replay_file = models.FileField(upload_to='replays', blank=True, null=True)
    game_steps = models.IntegerField()
    submitted_by = models.ForeignKey(User, on_delete=models.PROTECT, blank=True, null=True)
    arenaclient_log = models.FileField(upload_to=arenaclient_log_upload_to, blank=True, null=True)

    def __str__(self):
        return self.created.__str__()

    @property
    def duration_seconds(self):
        return (self.created - self.match.started).total_seconds()

    # this is not checked while the replay corruption is happening
    def validate_replay_file_requirement(self):
        if (self.has_winner() or self.is_tie()) and not self.replay_file:
            raise ValidationError('A win/loss or tie result must contain a replay file.')

    def clean(self, *args, **kwargs):
        # todo: if we ever re-enable this, then it needs to be
        # todo: called upon serializer validation in the arenaclient API
        # self.validate_replay_file_requirement() # disabled for now
        super().clean(*args, **kwargs)

    # some replays corrupt under linux currently.
    # if a replay file isn't supplied when it should be, then we assume it was corrupted
    # and therefore not uploaded with the result.
    def replay_file_corruption_detected(self):
        return (self.has_winner() or self.is_tie()) and not self.replay_file

    def has_winner(self):
        return self.type in (
            'Player1Win',
            'Player1Crash',
            'Player1TimeOut',
            'Player2Win',
            'Player2Crash',
            'Player2TimeOut')

    def winner_participant_number(self):
        if self.type in (
                'Player1Win',
                'Player2Crash',
                'Player2TimeOut'):
            return 1
        elif self.type in (
                'Player1Crash',
                'Player1TimeOut',
                'Player2Win'):
            return 2
        else:
            return 0

    def is_tie(self):
        return self.type == 'Tie'

    def get_winner_loser_bots(self):
        bot1, bot2 = self.get_participant_bots()
        if self.type in ('Player1Win', 'Player2Crash', 'Player2TimeOut'):
            return bot1, bot2
        elif self.type in ('Player2Win', 'Player1Crash', 'Player1TimeOut'):
            return bot2, bot1
        else:
            raise Exception('There was no winner or loser for this match.')

    def get_participants(self):
        first = Participant.objects.get(match=self.match, participant_number=1)
        second = Participant.objects.get(match=self.match, participant_number=2)
        return first, second

    def get_participant_bots(self):
        first, second = self.get_participants()
        return first.bot, second.bot

    def save(self, *args, **kwargs):
        # set winner
        if self.has_winner():
            self.winner = Participant.objects.get(match=self.match,
                                                  participant_number=self.winner_participant_number()).bot

        self.full_clean()  # ensure validation is run on save
        super().save(*args, **kwargs)

    def adjust_elo(self):
        if self.has_winner():
            winner, loser = self.get_winner_loser_bots()
            self._apply_elo_delta(ELO.calculate_elo_delta(winner.elo, loser.elo, 1.0), winner, loser)
        elif self.type == 'Tie':
            first, second = self.get_participant_bots()
            self._apply_elo_delta(ELO.calculate_elo_delta(first.elo, second.elo, 0.5), first, second)

    def get_initial_elos(self):
        first, second = self.get_participant_bots()
        return first.elo, second.elo

    def _apply_elo_delta(self, delta, bot1, bot2):
        delta = int(round(delta))
        bot1.elo += delta
        bot1.save()
        bot2.elo -= delta
        bot2.save()


def elo_graph_upload_to(instance, filename):
    return '/'.join(['graphs', '{0}.png'.format(instance.id)])


class StatsBots(models.Model):
    bot = models.ForeignKey(Bot, on_delete=models.CASCADE)
    win_perc = models.FloatField(validators=[validate_not_nan, validate_not_inf])
    crash_perc = models.FloatField(validators=[validate_not_nan, validate_not_inf])
    game_count = models.IntegerField()
    generated_at = models.DateTimeField()
    elo_graph = models.FileField(upload_to=elo_graph_upload_to, storage=OverwriteStorage(), blank=True,
                                 null=True)


class StatsBotMatchups(models.Model):
    bot = models.ForeignKey(Bot, on_delete=models.CASCADE)
    opponent = models.ForeignKey(Bot, on_delete=models.CASCADE, related_name='opponent_stats')
    win_perc = models.FloatField(validators=[validate_not_nan, validate_not_inf])
    win_count = models.IntegerField()
    game_count = models.IntegerField()
    generated_at = models.DateTimeField()
