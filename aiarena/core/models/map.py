from django.db import models

from aiarena.api.arenaclient.common.util import obtain_s3_filehash_or_default
from aiarena.core.models.competition import Competition
from aiarena.core.models.game_mode import GameMode


def map_file_upload_to(instance, filename):
    return "/".join(["maps", instance.name])


class Map(models.Model):
    name = models.CharField(max_length=50, unique=True)
    file = models.FileField(upload_to=map_file_upload_to)
    game_mode = models.ForeignKey(GameMode, on_delete=models.CASCADE, related_name="maps")
    competitions = models.ManyToManyField(Competition, related_name="maps", blank=True)
    """The competitions this map is used in."""
    enabled = models.BooleanField(default=True)
    """Whether this map is enabled for play.
     Note that when this is set to false, it doesn't necessarily mean that the map isn't in a competition's map pool.
     In this way the map could still be used for matches."""

    def __str__(self):
        return self.name

    @property
    def file_hash(self):
        return obtain_s3_filehash_or_default(self.file, default=None)
