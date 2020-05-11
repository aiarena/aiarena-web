import logging

from django.db import models

from aiarena.core.models import User

logger = logging.getLogger(__name__)


class ArenaClient(User):
    """Represents an arenaclient user"""
    trusted = models.BooleanField(default=False)
    """Whether this Arena Client is trusted. Only trusted Arena Clients are used to run ladder games."""
