import logging

from django.db import models
from django.db.models.signals import pre_save
from django.dispatch import receiver

from .competition import Competition
from .mixins import LockableModelMixin


logger = logging.getLogger(__name__)


class Round(models.Model, LockableModelMixin):
    """Represents a round of play within a competition"""

    number = models.IntegerField(blank=True, editable=False)
    competition = models.ForeignKey(Competition, on_delete=models.CASCADE)
    started = models.DateTimeField(auto_now_add=True, db_index=True)
    finished = models.DateTimeField(blank=True, null=True, db_index=True)
    complete = models.BooleanField(default=False)

    @property
    def name(self):
        return "Round " + str(self.number)

    def __str__(self):
        return self.name

    def mark_complete(self, finish_timestamp):
        """
        Mark this round as complete and set the finished timestamp.
        """
        if self.complete:
            # Nothing should call this method on an already completed round. Highlight the bug.
            raise ValueError(f"Round {self.id} is already complete")

        self.complete = True
        self.finished = finish_timestamp


@receiver(pre_save, sender=Round)
def pre_save_round(sender, instance, **kwargs):
    if instance.number is None:
        instance.number = Round.objects.filter(competition=instance.competition).count() + 1
