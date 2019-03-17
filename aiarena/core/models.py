from django.db import models
from django.contrib.auth.models import User


class Bot(models.Model):
    TERRAN = 'T'
    ZERG = 'Z'
    PROTOSS = 'P'
    RANDOM = 'R'
    RACES = (
        (TERRAN, 'Terran'),
        (ZERG, 'Zerg'),
        (PROTOSS, 'Protoss'),
        (RANDOM, 'Random'),
    )
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=50, unique=True)
    created = models.DateTimeField()
    updated = models.DateTimeField()
    active = models.BooleanField(default=False)
    elo = models.SmallIntegerField(default=1600)
    bot_zip = models.FileField()  # todo: limit public access to this file and customize upload location
    bot_zip_md5hash = models.CharField(max_length=50)
    plays_race = models.CharField(max_length=2, choices=RACES)

    def __str__(self):
        return self.name


class Map(models.Model):
    name = models.CharField(max_length=50, unique=True)
    file = models.FileField()

    def __str__(self):
        return self.name


# todo: structure for separate ladder types
class Match(models.Model):
    map = models.ForeignKey(Map, on_delete=models.PROTECT)
    created = models.DateTimeField()

    def __str__(self):
        return self.created


class Participant(models.Model):
    match = models.ForeignKey(Match, on_delete=models.CASCADE)
    participant_number = models.PositiveSmallIntegerField()
    bot = models.ForeignKey(Bot, on_delete=models.PROTECT, related_name='match_participations')

    def __str__(self):
        return self.bot.name


class Result(models.Model):
    PLAYER1WIN = 'P1W'
    PLAYER2WIN = 'P2W'
    PLAYER1CRASH = 'P1C'
    PLAYER2CRASH = 'P2C'
    GAMETIMEOUT = 'GTO'
    TIE = 'TIE'
    TYPES = (
        (PLAYER1WIN, 'P1W'),
        (PLAYER1WIN, 'P2W'),
        (PLAYER1CRASH, 'P1C'),
        (PLAYER2CRASH, 'P2C'),
        (GAMETIMEOUT, 'GTO'),
        (TIE, 'TIE'),
    )
    match = models.OneToOneField(Match, on_delete=models.CASCADE, related_name='result')
    winner = models.ForeignKey(Bot, on_delete=models.PROTECT, related_name='matches_won')
    type = models.CharField(max_length=3, choices=TYPES)
    created = models.DateTimeField()
    replay_file = models.FileField()  # todo: limit public access to this file and customize upload location

    def __str__(self):
        return self.bot.created
