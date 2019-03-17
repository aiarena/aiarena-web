from django.db import models
from django.contrib.auth.models import User


class Sc2Race(models.Model):
    name = models.CharField(max_length=50, unique=True)

    def __str__(self):
        return self.name


class Bot(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=50, unique=True)
    created = models.DateTimeField()
    updated = models.DateTimeField()
    active = models.BooleanField(default=False)
    elo = models.SmallIntegerField(default=1600)
    bot_zip = models.FileField()
    bot_zip_md5hash = models.CharField(max_length=50)
    plays_race = models.ForeignKey(Sc2Race, on_delete=models.PROTECT)

    def __str__(self):
        return self.name


class Map(models.Model):
    name = models.CharField(max_length=50, unique=True)
    file = models.FileField()

    def __str__(self):
        return self.name


# todo: populate database with result types
class ResultType(models.Model):
    name = models.CharField(max_length=50, unique=True)

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
    match = models.OneToOneField(Match, on_delete=models.CASCADE, related_name='result')
    winner = models.ForeignKey(Bot, on_delete=models.PROTECT, related_name='matches_won')
    type = models.ForeignKey(ResultType, on_delete=models.PROTECT)
    created = models.DateTimeField()

    def __str__(self):
        return self.bot.created
