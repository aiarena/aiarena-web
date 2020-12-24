import logging

from django.db import models

from .game import Game

logger = logging.getLogger(__name__)


class GameMode(models.Model):
    """ Represents a game mode for a game.
        Example: Starcraft 2's default melee game or a micro challenge game.'"""
    name = models.CharField(max_length=50)
    game = models.ForeignKey(Game, on_delete=models.CASCADE, related_name='game_modes')

    def __str__(self):
        return self.name

    class Meta:
        unique_together = (('name', 'game'),)
