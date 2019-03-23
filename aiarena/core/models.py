from django.contrib.auth.models import AbstractUser
from django.db import models


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
    active = models.BooleanField(default=False)
    elo = models.SmallIntegerField(default=1600)  # todo: auto-generate/readonly
    bot_zip = models.FileField(upload_to='bots')  # todo: limit public access to this file
    bot_zip_md5hash = models.CharField(max_length=50)  # todo: auto-generate/readonly
    plays_race = models.CharField(max_length=1, choices=RACES)
    type = models.CharField(max_length=32, choices=TYPES)

    def __str__(self):
        return self.name


class Map(models.Model):
    name = models.CharField(max_length=50, unique=True)
    file = models.FileField(upload_to='maps')

    def __str__(self):
        return self.name


# todo: structure for separate ladder types
class Match(models.Model):
    map = models.ForeignKey(Map, on_delete=models.PROTECT)
    created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.created


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
        return self.created
