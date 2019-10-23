import logging
import time
import uuid
from enum import Enum

from constance import config
from django.contrib.auth.models import AbstractUser
from django.contrib.sites.models import Site
from django.core.exceptions import ValidationError
from django.core.mail import send_mail
from django.db import models, transaction, connection
from django.db.models import F
from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from django.urls import reverse
from django.utils import timezone
from django.utils.html import escape
from private_storage.fields import PrivateFileField

from aiarena import settings
from aiarena.api.arenaclient.exceptions import NotEnoughAvailableBots, NoMaps, NotEnoughActiveBots, MaxActiveRounds, \
    NoCurrentSeason, MultipleCurrentSeasons, CurrentSeasonPaused, CurrentSeasonClosing
from aiarena.core.exceptions import BotNotInMatchException, BotAlreadyInMatchException
from aiarena.core.storage import OverwritePrivateStorage, OverwriteStorage
from aiarena.core.utils import calculate_md5_django_filefield
from aiarena.core.validators import validate_not_nan, validate_not_inf, validate_bot_name, validate_bot_zip_file
from aiarena.settings import ELO_START_VALUE, ELO, BOT_ZIP_MAX_SIZE

logger = logging.getLogger(__name__)


class LockableModelMixin:
    def lock_me(self):
        # todo: is there a better way to do this?
        self.__class__.objects.select_for_update().get(id=self.id)
        self.refresh_from_db()


def map_file_upload_to(instance, filename):
    return '/'.join(['maps', instance.name])


class Map(models.Model):
    name = models.CharField(max_length=50, unique=True)
    file = models.FileField(upload_to=map_file_upload_to, storage=OverwriteStorage())
    active = models.BooleanField(default=False)

    def __str__(self):
        return self.name

    @staticmethod
    def random_active():
        # todo: apparently this is really slow
        # https://stackoverflow.com/questions/962619/how-to-pull-a-random-record-using-djangos-orm#answer-962672
        return Map.objects.filter(active=True).order_by('?').first()

    def activate(self):
        self.active = True
        self.save()

    def deactivate(self):
        self.active = False
        self.save()


class User(AbstractUser):
    PATREON_LEVELS = (
        ('None', 'None'),
        ('Bronze', 'Bronze'),
        ('Silver', 'Silver'),
        ('Gold', 'Gold'),
        ('Platinum', 'Platinum'),
        ('Diamond', 'Diamond'),
    )
    email = models.EmailField(unique=True)
    service_account = models.BooleanField(default=False)
    patreon_level = models.CharField(max_length=16, choices=PATREON_LEVELS, default='None')

    def get_absolute_url(self):
        return reverse('author', kwargs={'pk': self.pk})

    def as_html_link(self):
        return '<a href="{0}">{1}</a>'.format(self.get_absolute_url(), escape(self.__str__()))


class Season(models.Model, LockableModelMixin):
    """ Represents a season of play in the context of a ladder """
    SEASON_STATUSES = (
        ('created', 'Created'),  # The initial state for a season. Functionally identical to paused.
        ('paused', 'Paused'),  # While a season is paused, existing rounds can be played, but no new ones are generated.
        ('open', 'Open'),  # When a season is open, new rounds can be generated and played.
        ('closing', 'Closing'),
        # When a season is closing, it's the same as paused except it will automatically move to closed when all rounds are finished.
        ('closed', 'Closed'),  # Functionally identical to paused, except not intended to change after this status.
    )
    date_created = models.DateTimeField(auto_now_add=True)
    date_opened = models.DateTimeField(blank=True, null=True)
    date_closed = models.DateTimeField(blank=True, null=True)
    status = models.CharField(max_length=16, choices=SEASON_STATUSES, default='created')

    def __str__(self):
        return self.id.__str__()

    @property
    def is_paused(self):
        return self.status == 'paused'

    @property
    def is_closing(self):
        return self.status == 'closing'

    def pause(self):
        self.status = 'paused'
        self.save()

    def open(self):
        if self.status == 'created':
            self.date_opened = timezone.now()
        self.status = 'open'
        self.save()

    def close(self):
        self.status = 'closing'
        self.save()

    def try_to_close(self):
        self.lock_me()

        if self.is_closing and Round.objects.filter(season=self, complete=False).count() == 0:
            self.status = 'closed'
            self.date_closed = timezone.now()
            self.save()

    @staticmethod
    def get_current_season():
        try:
            #  will fail if there is more than 1 current season or 0 current seasons
            return Season.objects.get(date_closed__isnull=True)
        except Season.DoesNotExist:
            raise NoCurrentSeason()  # todo: separate between core and API exceptions
        except Season.MultipleObjectsReturned:
            raise MultipleCurrentSeasons()  # todo: separate between core and API exceptions

    def get_absolute_url(self):
        return reverse('season', kwargs={'pk': self.pk})

    def as_html_link(self):
        return '<a href="{0}">{1}</a>'.format(self.get_absolute_url(), escape(self.__str__()))


class Round(models.Model, LockableModelMixin):
    """ Represents a round of play within a season """
    season = models.ForeignKey(Season, on_delete=models.CASCADE)  # todo: eob remove blank/null
    started = models.DateTimeField(auto_now_add=True)
    finished = models.DateTimeField(blank=True, null=True)
    complete = models.BooleanField(default=False)

    def __str__(self):
        return self.id.__str__()

    # if all the matches have been run, mark this as complete
    def update_if_completed(self):
        self.lock_me()

        # if there are no matches without results, this round is complete
        if Match.objects.filter(round=self, result__isnull=True).count() == 0:
            self.complete = True
            self.finished = timezone.now()
            self.save()
            Season.get_current_season().try_to_close()

    @staticmethod
    def max_active_rounds_reached():
        return Round.objects.filter(complete=False).count() >= config.MAX_ACTIVE_ROUNDS

    @staticmethod
    def generate_new():
        if Map.objects.filter(active=True).count() == 0:
            raise NoMaps()  # todo: separate between core and API exceptions
        if Bot.objects.filter(active=True).count() <= 1:  # need at least 2 active bots for a match
            raise NotEnoughActiveBots()  # todo: separate between core and API exceptions

        current_season = Season.get_current_season()
        if current_season.is_paused:
            raise CurrentSeasonPaused()
        if current_season.is_closing:  # we should technically never hit this
            raise CurrentSeasonClosing()

        new_round = Round.objects.create(season=Season.get_current_season())

        active_bots = Bot.objects.filter(active=True)
        already_processed_bots = []

        # loop through and generate matches for all active bots
        for bot1 in active_bots:
            already_processed_bots.append(bot1.id)
            for bot2 in Bot.objects.filter(active=True).exclude(id__in=already_processed_bots):
                Match.create(new_round, Map.random_active(), bot1, bot2)

    def get_absolute_url(self):
        return reverse('round', kwargs={'pk': self.pk})

    def as_html_link(self):
        return '<a href="{0}">{1}</a>'.format(self.get_absolute_url(), escape(self.__str__()))


# todo: structure for separate ladder types
class Match(models.Model):
    """ Represents a match between 2 bots. Usually this is within the context of a round, but doesn't have to be. """
    map = models.ForeignKey(Map, on_delete=models.PROTECT)
    created = models.DateTimeField(auto_now_add=True)
    started = models.DateTimeField(blank=True, null=True, editable=False)
    assigned_to = models.ForeignKey(User, on_delete=models.PROTECT, blank=True,
                                    null=True)  # todo: eob remove blank/null
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
                participations = MatchParticipation.objects.select_for_update().filter(match=self)
                for p in participations:
                    if p.bot.in_match:
                        return Match.StartResult.BOT_ALREADY_IN_MATCH

                for p in participations:
                    p.bot.enter_match(self)

                self.started = timezone.now()
                self.assigned_to = assign_to
                self.save()
                return Match.StartResult.SUCCESS
            else:
                return Match.StartResult.FAIL_ALREADY_STARTED

    @property
    def participant1(self):
        return self.matchparticipation_set.get(participant_number=1)

    @property
    def participant2(self):
        return self.matchparticipation_set.get(participant_number=2)

    @staticmethod
    def start_next_match(requesting_user):

        # todo: clean up this whole section

        Bot.timeout_overtime_bot_games()

        with connection.cursor() as cursor:
            # Lock the matches table
            # this needs to happen so that if we end up having to generate a new set of matches
            # then we don't hit a race condition
            # MySql also requires we lock any other tables we access as well.
            cursor.execute(
                "LOCK TABLES {0} WRITE, {1} WRITE, {2} WRITE, {3} WRITE, {4} READ, {5} READ".format(
                    Match._meta.db_table,
                    Round._meta.db_table,
                    MatchParticipation._meta.db_table,
                    Bot._meta.db_table,
                    Map._meta.db_table,
                    Season._meta.db_table))
            try:
                match = Match._locate_and_return_started_match(requesting_user)
                if match is None:
                    if Bot.objects.filter(active=True, in_match=False).count() < 2:
                        # All the active bots are already in a match
                        raise NotEnoughAvailableBots()
                    elif Round.max_active_rounds_reached():
                        raise MaxActiveRounds()
                    else:  # generate new round
                        Round.generate_new()
                        match = Match._locate_and_return_started_match(requesting_user)
                        if match is None:
                            cursor.execute("ROLLBACK")
                            raise Exception("Failed to start match for unknown reason.")
                        else:
                            return match
                else:
                    return match
            except:
                # ROLLBACK here so the UNLOCK statement doesn't commit changes
                cursor.execute("ROLLBACK")
                raise  # rethrow
            finally:
                # pass
                cursor.execute("UNLOCK TABLES;")

    @staticmethod
    def create(round, map, bot1, bot2):
        match = Match.objects.create(map=map, round=round)
        # create match participations
        MatchParticipation.objects.create(match=match, participant_number=1, bot=bot1)
        MatchParticipation.objects.create(match=match, participant_number=2, bot=bot2)
        return match

    # todo: let us specify the map
    @staticmethod
    def request_bot_match(bot, opponent=None):
        return Match.create(None, Map.random_active(), bot,
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
                    bot1 = match.matchparticipation_set.select_related().select_for_update().get(
                        participant_number=1).bot
                    bot1.leave_match(match.id)
                except BotNotInMatchException:
                    pass
                try:
                    bot2 = match.matchparticipation_set.select_related().select_for_update().get(
                        participant_number=2).bot
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
    name = models.CharField(max_length=50, unique=True, validators=[validate_bot_name, ])
    created = models.DateTimeField(auto_now_add=True)
    active = models.BooleanField(default=False)  # todo: change this to instead be an enrollment in a ladder?
    in_match = models.BooleanField(default=False)  # todo: move to ladder participant when multiple ladders comes in
    current_match = models.ForeignKey(Match, on_delete=models.PROTECT, blank=True, null=True,
                                      related_name='bots_currently_in_match')
    bot_zip = PrivateFileField(upload_to=bot_zip_upload_to, storage=OverwritePrivateStorage(base_url='/'),
                               max_file_size=BOT_ZIP_MAX_SIZE, validators=[validate_bot_zip_file, ])
    bot_zip_updated = models.DateTimeField(editable=False)
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
                ' Each user can only have ' + str(
                    config.MAX_USER_BOT_COUNT_ACTIVE_PER_RACE) + ' active bot(s) per race.')

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

    def expected_executable_filename(self):
        """
        The expected file name that should be run to start the bot.
        e.g. for a cpp binary bot, this would be Bot.exe
        :return:
        """
        if self.type == 'cppwin32':
            return f'{self.name}.exe'
        elif self.type == 'cpplinux':
            return self.name
        elif self.type == 'dotnetcore':
            return f'{self.name}.dll'
        elif self.type == 'java':
            return f'{self.name}.jar'
        elif self.type == 'nodejs':
            return f'{self.name}.js'
        elif self.type == 'python':
            return 'run.py'

    def disable_and_sent_alert(self):
        self.active = False
        self.save()
        try:
            send_mail(  # todo: template this
                'AI Arena - ' + self.name + ' deactivated due to crashing',
                'Dear ' + self.user.username + ',\n'
                                               '\n'
                                               'We are emailing you to let you know that your bot '
                                               '"' + self.name + '" has reached our consecutive crash limit and hence been deactivated.\n'
                                                                 'Please log into ai-arena.net at your convenience to address the issue.\n'
                                                                 'Bot logs are available for download when logged in on the bot''s page here: '
                + settings.SITE_PROTOCOL + '://' + Site.objects.get_current().domain
                + reverse('bot', kwargs={'pk': self.id}) + '\n'
                                                           '\n'
                                                           'Kind regards,\n'
                                                           'AI Arena Staff',
                settings.DEFAULT_FROM_EMAIL,
                [self.user.email],
                fail_silently=False,
            )
        except Exception as e:
            logger.exception(e)

    def current_season_participation(self):
        return self.seasonparticipation_set.get(season=Season.get_current_season())


_UNSAVED_BOT_ZIP_FILEFIELD = 'unsaved_bot_zip_filefield'
_UNSAVED_BOT_DATA_FILEFIELD = 'unsaved_bot_data_filefield'


# The following methods will temporarily store the bot_zip and bot_data files while we wait for the Bot model to be
# saved in order to generate an ID, which can then be used in the path for the bot_zip name
# This needs to happen because we want to use the model ID in the file path, but until the model is saved, it doesn't
# have an ID.
@receiver(pre_save, sender=Bot)
def pre_save_bot(sender, instance, **kwargs):
    # If the Bot model hasn't been created yet (i.e. it's missing its ID) then set any files aside for the time being
    if not instance.pk and not hasattr(instance, _UNSAVED_BOT_ZIP_FILEFIELD):
        setattr(instance, _UNSAVED_BOT_ZIP_FILEFIELD, instance.bot_zip)
        instance.bot_zip = None
        instance.bot_zip_updated = timezone.now()

    # bot data
    if not instance.pk and not hasattr(instance, _UNSAVED_BOT_DATA_FILEFIELD) and instance.bot_data:
        setattr(instance, _UNSAVED_BOT_DATA_FILEFIELD, instance.bot_data)
        instance.bot_data = None


@receiver(post_save, sender=Bot)
def post_save_bot(sender, instance, created, **kwargs):
    # bot zip
    if created and hasattr(instance, _UNSAVED_BOT_ZIP_FILEFIELD):
        instance.bot_zip = getattr(instance, _UNSAVED_BOT_ZIP_FILEFIELD)
        post_save.disconnect(pre_save_bot, sender=sender)
        instance.save()
        post_save.connect(pre_save_bot, sender=sender)
        # delete the saved instance
        instance.__dict__.pop(_UNSAVED_BOT_ZIP_FILEFIELD)

    # bot data
    if created and hasattr(instance, _UNSAVED_BOT_DATA_FILEFIELD):
        instance.bot_data = getattr(instance, _UNSAVED_BOT_DATA_FILEFIELD)
        post_save.disconnect(pre_save_bot, sender=sender)
        instance.save()
        post_save.connect(pre_save_bot, sender=sender)
        # delete the saved instance
        instance.__dict__.pop(_UNSAVED_BOT_DATA_FILEFIELD)

    # Re-calculate the file hashes if required.
    if instance.bot_zip:
        bot_zip_hash = calculate_md5_django_filefield(instance.bot_zip)
        if instance.bot_zip_md5hash != bot_zip_hash:
            instance.bot_zip_md5hash = bot_zip_hash
            instance.bot_zip_updated = timezone.now()
            post_save.disconnect(pre_save_bot, sender=sender)
            instance.save()
            post_save.connect(pre_save_bot, sender=sender)

    if instance.bot_data:
        bot_data_hash = calculate_md5_django_filefield(instance.bot_data)
        if instance.bot_data_md5hash != bot_data_hash:
            instance.bot_data_md5hash = bot_data_hash
            post_save.disconnect(pre_save_bot, sender=sender)
            instance.save()
            post_save.connect(pre_save_bot, sender=sender)
    elif instance.bot_data_md5hash is not None:
        instance.bot_data_md5hash = None
        post_save.disconnect(pre_save_bot, sender=sender)
        instance.save()
        post_save.connect(pre_save_bot, sender=sender)

    # register a season participation if the bot has been activated
    if instance.active and instance.seasonparticipation_set.filter(season=Season.get_current_season()).count() == 0:
        SeasonParticipation.objects.create(season=Season.get_current_season(), bot=instance)


class SeasonParticipation(models.Model):
    season = models.ForeignKey(Season, on_delete=models.CASCADE)
    bot = models.ForeignKey(Bot, on_delete=models.PROTECT)
    elo = models.SmallIntegerField(default=ELO_START_VALUE)


def match_log_upload_to(instance, filename):
    return '/'.join(['match-logs', str(instance.id)])


class MatchParticipation(models.Model):
    RESULT_TYPES = (
        ('none', 'None'),
        ('win', 'Win'),
        ('loss', 'Loss'),
        ('tie', 'Tie'),
    )
    CAUSE_TYPES = (
        ('game_rules', 'Game Rules'),  # This represents the game handing out a result
        ('crash', 'Crash'),  # A bot crashed
        ('timeout', 'Timeout'),  # A bot timed out
        ('race_mismatch', 'Race Mismatch'),  # A bot joined the match with the wrong race
        ('match_cancelled', 'Match Cancelled'),  # The match was cancelled
        ('initialization_failure', 'Initialization Failure'),  # A bot failed to initialize
        ('error', 'Error'),
    # There was an unspecified error running the match (this should only be paired with a 'none' result)

    )
    match = models.ForeignKey(Match, on_delete=models.CASCADE)
    participant_number = models.PositiveSmallIntegerField()
    bot = models.ForeignKey(Bot, on_delete=models.PROTECT)
    resultant_elo = models.SmallIntegerField(null=True)
    elo_change = models.SmallIntegerField(null=True)
    match_log = PrivateFileField(upload_to=match_log_upload_to, storage=OverwritePrivateStorage(base_url='/'),
                                 blank=True, null=True)
    avg_step_time = models.FloatField(blank=True, null=True, validators=[validate_not_nan, validate_not_inf])
    result = models.CharField(max_length=32, choices=RESULT_TYPES, blank=True, null=True)
    result_cause = models.CharField(max_length=32, choices=CAUSE_TYPES, blank=True, null=True)

    def __str__(self):
        return self.bot.name

    @property
    def step_time_ms(self):
        return (self.avg_step_time if self.avg_step_time is not None else 0) * 1000

    @property
    def crashed(self):
        return self.result == 'loss' and self.result_cause in ['crash', 'timeout', 'initialization_failure']

    @property
    def season_participant(self):
        return self.match.round.season.seasonparticipation_set.get(bot=self.bot)

    def calculate_relative_result(self, result_type):
        if result_type in ['MatchCancelled', 'InitializationError', 'Error']:
            return 'none'
        elif result_type in ['Player1Win', 'Player2Crash', 'Player2TimeOut', 'Player2RaceMismatch']:
            return 'win' if self.participant_number == 1 else 'loss'
        elif result_type in ['Player2Win', 'Player1Crash', 'Player1TimeOut', 'Player1RaceMismatch']:
            return 'win' if self.participant_number == 2 else 'loss'
        elif result_type == 'Tie':
            return 'tie'
        else:
            raise Exception('Unrecognized result type!')

    def calculate_relative_result_cause(self, result_type):
        if result_type in ['Player1Win', 'Player2Win', 'Tie']:
            return 'game_rules'
        elif result_type in ['Player1Crash', 'Player2Crash']:
            return 'crash'
        elif result_type in ['Player1TimeOut', 'Player2TimeOut']:
            return 'timeout'
        elif result_type in ['Player1RaceMismatch', 'Player2RaceMismatch']:
            return 'race_mismatch'
        elif result_type == 'MatchCancelled':
            return 'match_cancelled'
        elif result_type == 'InitializationError':
            return 'initialization_failure'
        elif result_type == 'Error':
            return 'error'
        else:
            raise Exception('Unrecognized result type!')


def replay_file_upload_to(instance, filename):
    return '/'.join(['replays',
                     f'{instance.match_id}'
                     f'_{instance.match.matchparticipation_set.get(participant_number=1).bot.name}'
                     f'vs{instance.match.matchparticipation_set.get(participant_number=2).bot.name}'
                     f'_{instance.match.map.name}.SC2Replay'])


def arenaclient_log_upload_to(instance, filename):
    return '/'.join(['arenaclient-logs', '{0}_arenaclientlog.zip'.format(instance.match_id)])


class Result(models.Model):
    TYPES = (
        ('MatchCancelled', 'MatchCancelled'),
        ('InitializationError', 'InitializationError'),
        ('Error', 'Error'),
        ('Player1Win', 'Player1Win'),
        ('Player1Crash', 'Player1Crash'),
        ('Player1TimeOut', 'Player1TimeOut'),
        ('Player1RaceMismatch', 'Player1RaceMismatch'),
        ('Player1Surrender', 'Player1Surrender'),
        ('Player2Win', 'Player2Win'),
        ('Player2Crash', 'Player2Crash'),
        ('Player2TimeOut', 'Player2TimeOut'),
        ('Player2RaceMismatch', 'Player2RaceMismatch'),
        ('Player2Surrender', 'Player2Surrender'),
        ('Tie', 'Tie'),
    )
    match = models.OneToOneField(Match, on_delete=models.CASCADE, related_name='result')
    winner = models.ForeignKey(Bot, on_delete=models.PROTECT, related_name='matches_won', blank=True, null=True)
    type = models.CharField(max_length=32, choices=TYPES)
    created = models.DateTimeField(auto_now_add=True)
    replay_file = models.FileField(upload_to=replay_file_upload_to, blank=True, null=True)
    game_steps = models.IntegerField()
    submitted_by = models.ForeignKey(User, on_delete=models.PROTECT, blank=True, null=True)
    arenaclient_log = models.FileField(upload_to=arenaclient_log_upload_to, blank=True, null=True)

    def __str__(self):
        return self.created.__str__()

    @property
    def duration_seconds(self):
        return (self.created - self.match.started).total_seconds()

    @property
    def game_time_formatted(self):
        return time.strftime("%H:%M:%S", time.gmtime(self.game_steps / 22.4))

    @property
    def participant1(self):
        return self.match.participant1

    @property
    def participant2(self):
        return self.match.participant2

    # this is not checked while the replay corruption is happening
    def validate_replay_file_requirement(self):
        if (self.has_winner() or self.is_tie()) and not self.replay_file:
            raise ValidationError('A win/loss or tie result must contain a replay file.')

    def clean(self, *args, **kwargs):
        # todo: if we ever re-enable this, then it needs to be
        # todo: called upon serializer validation in the arenaclient API
        # self.validate_replay_file_requirement() # disabled for now
        super().clean(*args, **kwargs)

    def has_winner(self):
        return self.type in (
            'Player1Win',
            'Player1Crash',
            'Player1TimeOut',
            'Player1Surrender',
            'Player2Win',
            'Player2Crash',
            'Player2TimeOut',
            'Player2Surrender')

    def winner_participant_number(self):
        if self.type in (
                'Player1Win',
                'Player2Crash',
                'Player2TimeOut',
                'Player2Surrender'):
            return 1
        elif self.type in (
                'Player1Crash',
                'Player1TimeOut',
                'Player1Surrender',
                'Player2Win'):
            return 2
        else:
            return 0

    def is_tie(self):
        return self.type == 'Tie'

    def is_timeout(self):
        return self.type == 'Player1TimeOut' or self.type == 'Player2TimeOut'

    def is_crash(self):
        return self.type == 'Player1Crash' or self.type == 'Player2Crash'

    def is_crash_or_timeout(self):
        return self.is_crash() or self.is_timeout()

    def get_causing_participant_of_crash_or_timeout_result(self):
        if self.type == 'Player1TimeOut' or self.type == 'Player1Crash':
            return self.participant1
        elif self.type == 'Player2TimeOut' or self.type == 'Player2Crash':
            return self.participant2
        else:
            return None

    def get_winner_loser_season_participants(self):
        bot1, bot2 = self.get_season_participants()
        if self.type in ('Player1Win', 'Player2Crash', 'Player2TimeOut', 'Player2Surrender'):
            return bot1, bot2
        elif self.type in ('Player2Win', 'Player1Crash', 'Player1TimeOut', 'Player1Surrender'):
            return bot2, bot1
        else:
            raise Exception('There was no winner or loser for this match.')

    def get_winner_loser_bots(self):
        bot1, bot2 = self.get_match_participant_bots()
        if self.type in ('Player1Win', 'Player2Crash', 'Player2TimeOut', 'Player2Surrender'):
            return bot1, bot2
        elif self.type in ('Player2Win', 'Player1Crash', 'Player1TimeOut', 'Player1Surrender'):
            return bot2, bot1
        else:
            raise Exception('There was no winner or loser for this match.')

    def get_season_participants(self):
        """Returns the SeasonParticipant models for the MatchParticipants"""
        first = MatchParticipation.objects.get(match=self.match, participant_number=1)
        second = MatchParticipation.objects.get(match=self.match, participant_number=2)
        return first.season_participant, second.season_participant

    def get_match_participants(self):
        first = MatchParticipation.objects.get(match=self.match, participant_number=1)
        second = MatchParticipation.objects.get(match=self.match, participant_number=2)
        return first, second

    def get_match_participant_bots(self):
        first, second = self.get_match_participants()
        return first.bot, second.bot

    def save(self, *args, **kwargs):
        # set winner
        if self.has_winner():
            self.winner = MatchParticipation.objects.get(match=self.match,
                                                         participant_number=self.winner_participant_number()).bot

        self.full_clean()  # ensure validation is run on save
        super().save(*args, **kwargs)

    def adjust_elo(self):
        if self.has_winner():
            sp_winner, sp_loser = self.get_winner_loser_season_participants()
            self._apply_elo_delta(ELO.calculate_elo_delta(sp_winner.elo, sp_loser.elo, 1.0), sp_winner, sp_loser)
        elif self.type == 'Tie':
            sp_first, sp_second = self.get_season_participants()
            self._apply_elo_delta(ELO.calculate_elo_delta(sp_first.elo, sp_second.elo, 0.5), sp_first, sp_second)

    def get_initial_elos(self):
        first, second = self.get_season_participants()
        return first.elo, second.elo

    def _apply_elo_delta(self, delta, sp1, sp2):
        delta = int(round(delta))
        sp1.elo += delta
        sp1.save()
        sp2.elo -= delta
        sp2.save()


def elo_graph_upload_to(instance, filename):
    return '/'.join(['graphs', '{0}_{1}.png'.format(instance.bot.id, instance.bot.name)])


# todo: rename to BotStats
class StatsBots(models.Model):
    bot = models.ForeignKey(Bot, on_delete=models.CASCADE)
    win_perc = models.FloatField(validators=[validate_not_nan, validate_not_inf])
    crash_perc = models.FloatField(validators=[validate_not_nan, validate_not_inf])
    game_count = models.IntegerField()
    generated_at = models.DateTimeField()
    elo_graph = models.FileField(upload_to=elo_graph_upload_to, storage=OverwriteStorage(), blank=True,
                                 null=True)


# todo: rename to BotMatchupStats
class StatsBotMatchups(models.Model):
    bot = models.ForeignKey(Bot, on_delete=models.CASCADE)
    opponent = models.ForeignKey(Bot, on_delete=models.CASCADE, related_name='opponent_stats')
    win_perc = models.FloatField(validators=[validate_not_nan, validate_not_inf])
    win_count = models.IntegerField()
    game_count = models.IntegerField()
    generated_at = models.DateTimeField()
