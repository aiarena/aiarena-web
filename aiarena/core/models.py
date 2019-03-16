from django.db import models
from django.contrib.auth.models import User


class Sc2Race(models.Model):
    name = models.CharField(max_length=50, unique=True)


class Bot(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=50)
    created_date = models.DateTimeField()
    updated_date = models.DateTimeField()
    active = models.BooleanField(default=False)
    elo = models.SmallIntegerField(default=1600)
    bot_zip = models.FileField()
    bot_zip_md5hash = models.CharField(max_length=50)
    plays_race = models.ForeignKey(Sc2Race, on_delete=models.PROTECT)


class Map(models.Model):
    name = models.CharField(max_length=50, unique=True)
    file = models.FileField()


class ResultType(models.Model):
    name = models.CharField(max_length=50, unique=True)


class Result(models.Model):
    bot1 = models.ForeignKey(Bot, on_delete=models.PROTECT, related_name='bot1')
    bot2 = models.ForeignKey(Bot, on_delete=models.PROTECT, related_name='bot2')
    winner = models.ForeignKey(Bot, on_delete=models.PROTECT, related_name='winner')
    result_type = models.ForeignKey(ResultType, on_delete=models.PROTECT)
    map = models.ForeignKey(Map, on_delete=models.PROTECT)
    datetime = models.DateTimeField()
