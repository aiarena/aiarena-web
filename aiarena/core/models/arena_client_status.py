import logging

from django.db import models

from . import ArenaClient


logger = logging.getLogger(__name__)


class ArenaClientStatus(models.Model):
    STATUS_TYPES = (
        ("idle", "Idle"),
        ("starting_game", "Starting Game"),
        ("playing_game", "In Game"),
        ("submitting_result", "Submitting Result"),
    )
    arenaclient = models.ForeignKey(ArenaClient, on_delete=models.CASCADE, related_name="statuses")
    """The ArenaClient this status pertains to."""
    status = models.CharField(max_length=17, choices=STATUS_TYPES)
    """The running status of the ArenaClient."""
    logged_at = models.DateTimeField(auto_now_add=True, db_index=True)
    """The datetime this status was logged at."""
