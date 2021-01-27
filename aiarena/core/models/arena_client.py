import logging

from django.db import models

from .user import User

logger = logging.getLogger(__name__)


class ArenaClient(User):
    """Represents an arenaclient user"""
    trusted = models.BooleanField(default=False)
    """Whether this Arena Client is trusted. Only trusted Arena Clients are used to run ladder games."""
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='arenaclients')
    """The user that owns this ArenaClient"""

    class Meta:
        verbose_name = 'ArenaClient'
