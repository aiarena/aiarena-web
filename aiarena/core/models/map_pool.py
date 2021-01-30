from django.db import models

from aiarena.core.models import Map


class MapPool(models.Model):
    name = models.CharField(max_length=50, unique=True)
    maps = models.ManyToManyField(Map, related_name='map_pools')

    def __str__(self):
        return self.name
