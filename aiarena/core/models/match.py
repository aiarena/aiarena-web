import logging

from django.db import models
from django.db.models.signals import m2m_changed, post_delete
from django.dispatch import receiver

from .map import Map
from .match_tag import MatchTag
from .mixins import LockableModelMixin, RandomManagerMixin
from .round import Round
from .user import User


logger = logging.getLogger(__name__)


# todo: structure for separate ladder types
class Match(models.Model, LockableModelMixin, RandomManagerMixin):
    """Represents a match between 2 bots. Usually this is within the context of a round, but doesn't have to be."""

    result = models.OneToOneField("Result", on_delete=models.CASCADE, related_name="match", null=True)
    map = models.ForeignKey(Map, on_delete=models.PROTECT)
    created = models.DateTimeField(auto_now_add=True, db_index=True)
    # todo: the functionality of the started and first_started fields does not appear to be fully implemented
    started = models.DateTimeField(blank=True, null=True, editable=False, db_index=True)
    first_started = models.DateTimeField(blank=True, null=True, editable=False, db_index=True)
    """The first time this match started. Different from the started field when multiple runs are attempted."""
    assigned_to = models.ForeignKey(
        User, on_delete=models.PROTECT, blank=True, null=True, related_name="assigned_matches"
    )
    round = models.ForeignKey(Round, on_delete=models.CASCADE, blank=True, null=True)
    requested_by = models.ForeignKey(
        User, on_delete=models.SET_NULL, blank=True, null=True, related_name="requested_matches"
    )
    require_trusted_arenaclient = models.BooleanField(default=True)
    """
    Whether this match should require it be run on a trusted arena client
    IMPORTANT: This is only a flag to force the use of a trusted client.
    This can be false and other factors can still cause the match to be run on a trusted client.
    """
    tags = models.ManyToManyField(MatchTag, blank=True)

    def __str__(self):
        return self.id.__str__()

    @property
    def participant1(self):
        return self.matchparticipation_set.get(participant_number=1)

    @property
    def participant2(self):
        return self.matchparticipation_set.get(participant_number=2)

    @property
    def is_requested(self):
        return self.requested_by is not None

    @property
    def is_already_started(self):
        return self.started is not None

    @property
    def status(self):
        from .result import Result  # avoid circular import

        try:
            finished = self.result is not None
        except Result.DoesNotExist:
            finished = False
        if finished:
            return "Finished"
        elif self.started:
            return "Started"
        else:
            return "Queued"


@receiver(m2m_changed, sender=Match.tags.through)
def delete_orphan_match_tags(sender, **kwargs):
    # when something is removed from the m2m:
    if kwargs["action"] == "post_remove":
        # select removed tags and check if they are not linked to any Match, and delete it
        for mt in MatchTag.objects.filter(pk__in=kwargs["pk_set"]):
            if not mt.match_set.all():
                mt.delete()


@receiver(post_delete, sender=Match)
def delete_result_on_match_delete(sender, instance, **kwargs):
    result = instance.result
    if result:
        result.delete()
