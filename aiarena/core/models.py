import logging

from django.contrib.auth.models import AbstractUser
from django.core.exceptions import ValidationError
from django.db import models
from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from django.urls import reverse
from private_storage.fields import PrivateFileField

from aiarena.core.storage import OverwritePrivateStorage
from aiarena.core.utils import calculate_md5
from aiarena.settings import ELO_START_VALUE
from django.utils.html import escape
logger = logging.getLogger(__name__)


class User(AbstractUser):
    email = models.EmailField(unique=True)
    serviceaccount = models.BooleanField(default=0)


def bot_zip_upload_to(instance, filename):
    return '/'.join(['bots', str(instance.id), 'bot_zip'])


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
    elo = models.SmallIntegerField(default=ELO_START_VALUE)
    bot_zip = PrivateFileField(upload_to=bot_zip_upload_to, storage=OverwritePrivateStorage(base_url='/'),
                               max_file_size=1024 * 1024 * 50)  # max_file_size = 50MB
    bot_zip_md5hash = models.CharField(max_length=32, editable=False)
    plays_race = models.CharField(max_length=1, choices=RACES)
    type = models.CharField(max_length=32, choices=TYPES)

    def calc_bot_zip_md5hash(self):
        self.bot_zip_md5hash = calculate_md5(self.bot_zip.open(mode='rb'))

    # todo: once multiple ladders comes in, this will need to be updated to 1 bot race per ladder per user.
    def validate_one_bot_race_per_user(self):
        if Bot.objects.filter(user=self.user, plays_race=self.plays_race).exists() and not self.pk:
            raise ValidationError(
                'A bot playing that race already exists for this user. '
                'Each user can only have 1 bot per race.')

    def save(self, *args, **kwargs):
        self.calc_bot_zip_md5hash()
        super(Bot, self).save(*args, **kwargs)

    def clean(self):
        self.validate_one_bot_race_per_user() # todo: do this on bot activation instead

    def __str__(self):
        return self.name

    @staticmethod
    def random_active():
        # todo: apparently this is really slow
        # https://stackoverflow.com/questions/962619/how-to-pull-a-random-record-using-djangos-orm#answer-962672
        return Bot.objects.filter(active=True).order_by('?').first()

    @staticmethod
    def active_count():
        return Bot.objects.filter(active=True).count()

    def random_active_excluding_self(self):
        if Bot.active_count() <= 1:
            raise RuntimeError("I am the only bot.")
        return Bot.objects.filter(active=True).exclude(id=self.id).order_by('?').first()

    def get_absolute_url(self):
        return reverse('bot', kwargs={'pk': self.pk})

    def as_html_link(self):
        return '<a href="{0}">{1}</a>'.format(self.get_absolute_url(), escape(self.__str__()))


_UNSAVED_FILEFIELD = 'unsaved__filefield'


# The following methods will temporarily store the bot_zip file  while we wait for the Bot model to be saved
# in order to generate an ID, which can then be used in the bot_zip file name
@receiver(pre_save, sender=Bot)
def skip_saving_bot_zip_file(sender, instance, **kwargs):
    if not instance.pk and not hasattr(instance, _UNSAVED_FILEFIELD):
        setattr(instance, _UNSAVED_FILEFIELD, instance.bot_zip)
        instance.bot_zip = None


@receiver(post_save, sender=Bot)
def save_bot_zip_file(sender, instance, created, **kwargs):
    if created and hasattr(instance, _UNSAVED_FILEFIELD):
        instance.bot_zip = getattr(instance, _UNSAVED_FILEFIELD)
        instance.save()
        # delete the saved instance
        instance.__dict__.pop(_UNSAVED_FILEFIELD)


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


# todo: structure for separate ladder types
class Match(models.Model):
    map = models.ForeignKey(Map, on_delete=models.PROTECT)
    created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.id.__str__()


class Participant(models.Model):
    match = models.ForeignKey(Match, on_delete=models.CASCADE)
    participant_number = models.PositiveSmallIntegerField()
    bot = models.ForeignKey(Bot, on_delete=models.PROTECT, related_name='match_participations')
    resultant_elo = models.SmallIntegerField(null=True)

    def update_resultant_elo(self):
        self.resultant_elo = self.bot.elo
        self.save()

    def __str__(self):
        return self.bot.name


class Result(models.Model):
    TYPES = (
        ('InitializationError', 'InitializationError'),
        ('Timeout', 'Timeout'),
        ('ProcessingReplay', 'ProcessingReplay'),
        ('Player1Win', 'Player1Win'),
        ('Player1Crash', 'Player1Crash'),
        ('Player1TimeOut', 'Player1TimeOut'),
        ('Player2Win', 'Player2Win'),
        ('Player2Crash', 'Player2Crash'),
        ('Player2TimeOut', 'Player2TimeOut'),
        ('Tie', 'Tie'),
        ('Error', 'Error'),
    )
    match = models.OneToOneField(Match, on_delete=models.CASCADE, related_name='result')
    winner = models.ForeignKey(Bot, on_delete=models.PROTECT, related_name='matches_won', blank=True, null=True)
    type = models.CharField(max_length=32, choices=TYPES)
    created = models.DateTimeField(auto_now_add=True)
    replay_file = models.FileField(
        upload_to='replays')
    duration = models.IntegerField()

    def __str__(self):
        return self.created.__str__()

    def has_winner(self):
        return self.type in (
            'Player1Win',
            'Player1Crash',
            'Player1TimeOut',
            'Player2Win',
            'Player2Crash',
            'Player2TimeOut')

    def get_winner_loser_bots(self):
        bot1, bot2 = self.get_participant_bots()
        if self.type in ('Player1Win', 'Player2Crash', 'Player2TimeOut'):
            return bot1, bot2
        elif self.type in ('Player2Win', 'Player1Crash', 'Player1TimeOut'):
            return bot2, bot1
        else:
            raise Exception('There was no winner or loser for this match.')

    def get_participants(self):
        first = Participant.objects.filter(match=self.match, participant_number=1)
        second = Participant.objects.filter(match=self.match, participant_number=2)

        assert (first.count() == 1)
        assert (second.count() == 1)
        return first[0], second[0]

    def get_participant_bots(self):
        first, second = self.get_participants()
        return first.bot, second.bot

    # todo: validate that if the result type is either a timeout or tie, then there's no winner set etc
    # todo: use a model form
