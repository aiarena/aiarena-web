import logging
from typing import List

from django.db import models
from private_storage.fields import PrivateFileField
from django.db.models.expressions import Window
from django.db.models.functions import RowNumber
from django.db.models import F

from aiarena.core.models.competition import Competition

from .match import Match
from .match_participation import MatchParticipation
from ..storage import OverwritePrivateStorage

logger = logging.getLogger(__name__)


class RelativeResult(models.Model):
    """
    Utility model for a result from a specific participant's perspective
    Result type is displayed as Win or Loss with the reason appended.
    e.g. Loss - Crash
    """
    me = models.ForeignKey(MatchParticipation, on_delete=models.PROTECT, related_name='relative_result_me')
    match = models.ForeignKey(Match, on_delete=models.PROTECT, related_name='relative_result_match')
    started = models.DateTimeField()
    opponent = models.ForeignKey(MatchParticipation, on_delete=models.PROTECT, related_name='relative_result_opponent')
    result = models.CharField(max_length=32, choices=MatchParticipation.RESULT_TYPES)
    result_cause = models.CharField(max_length=32, choices=MatchParticipation.CAUSE_TYPES)
    elo_change = models.SmallIntegerField()
    avg_step_time = models.FloatField()
    game_time_formatted = models.CharField(max_length=32)
    game_steps = models.IntegerField()
    replay_file = models.FileField()
    match_log = PrivateFileField(storage=OverwritePrivateStorage(base_url='/'))

    class Meta:
        managed = False
    
    @classmethod
    def with_row_number(cls, bot_ids: List[int], competition: Competition):
        return (cls.objects.all()
                .filter(me__bot__id__in=bot_ids, match__requested_by__isnull=True, match__round__competition=competition)
                .annotate(
                        row_number=Window(
                            expression=RowNumber(), partition_by=[F("me__bot__id")], order_by=[F("started").desc()]
                    )
                ).values("me__bot__id", "row_number", "elo_change"))
