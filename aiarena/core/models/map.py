from django.db import models

from aiarena.core.models.competition import Competition
from aiarena.core.models.game_mode import GameMode
from aiarena.core.storage import OverwriteStorage


def map_file_upload_to(instance, filename):
    return '/'.join(['maps', instance.name])


class Map(models.Model):
    name = models.CharField(max_length=50, unique=True)
    file = models.FileField(upload_to=map_file_upload_to, storage=OverwriteStorage())
    game_mode = models.ForeignKey(GameMode, on_delete=models.CASCADE, related_name='maps')
    competitions = models.ManyToManyField(Competition, related_name='maps', blank=True)
    """The competitions this map is used in."""

    def __str__(self):
        return self.name
