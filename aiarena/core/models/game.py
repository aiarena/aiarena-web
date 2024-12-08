import logging

from django.db import models


logger = logging.getLogger(__name__)


class Game(models.Model):
    """Represents a playable game such as StarCraft 2"""

    name = models.CharField(max_length=50, unique=True)
    map_file_extension = models.CharField(
        max_length=20, default=".SC2Map", help_text="The file extension to use for map files for this game"
    )

    def __str__(self):
        return self.name
