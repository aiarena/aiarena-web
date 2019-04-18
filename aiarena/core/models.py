from django.contrib.auth.models import AbstractUser
from django.core.exceptions import ValidationError
from django.db import models

from aiarena.core.utils import calculate_md5


class User(AbstractUser):
    email = models.EmailField(unique=True)


class Bot(models.Model):
    RACES = (
        ('T', 'Terran'),
        ('Z', 'Zerg'),
        ('P', 'Protoss'),
        ('R', 'Random'),
    )
    TYPES = (
        ('Python', 'Python'),
    )
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=50, unique=True)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    active = models.BooleanField(default=False)  # todo: change this to instead be an enrollment in a ladder?
    elo = models.SmallIntegerField(default=1600)  # todo: auto-generate/readonly
    bot_zip = models.FileField(upload_to='bots')  # todo: limit public access to this file
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
        self.validate_one_bot_race_per_user()

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

    def __str__(self):
        return self.bot.name


class Result(models.Model):
    TYPES = (
        ('P1W', 'Player1Win'),
        ('P2W', 'Player2Win'),
        ('P1C', 'Player1Crash'),
        ('P2C', 'Player2Crash'),
        ('GTO', 'GameTimeout'),
        ('TIE', 'Tie'),
    )
    match = models.OneToOneField(Match, on_delete=models.CASCADE, related_name='result')
    winner = models.ForeignKey(Bot, on_delete=models.PROTECT, related_name='matches_won')
    type = models.CharField(max_length=3, choices=TYPES)
    created = models.DateTimeField(auto_now_add=True)
    replay_file = models.FileField(
        upload_to='replays')  # todo: limit public access to this file and customize upload location

    def __str__(self):
        return self.created.__str__()
