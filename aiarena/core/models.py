from django.db import models
from django.contrib.auth.models import User


class Bot(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=50)
    active = models.BooleanField(default=False)
    elo = models.SmallIntegerField(default=1600)
