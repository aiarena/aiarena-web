from django.db import models

from aiarena.core.models import Map


class MapPool(models.Model):
    name = models.CharField(max_length=50, unique=True)
    maps = models.ManyToManyField(Map, related_name="map_pools")
    enabled = models.BooleanField(default=True)
    """Whether this map pool is enabled for play. Currently this only effects match requests."""

    def __str__(self):
        return self.name
