import logging

from constance import config
from django.db import models, transaction
from django.db.models.signals import pre_save
from django.dispatch import receiver
from django.urls import reverse
from django.utils import timezone
from django.utils.html import escape
from django.utils.safestring import mark_safe

from .map import Map
from .mixins import LockableModelMixin
from .competition import Competition

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

    # if all the matches have been run, mark this as complete
    def update_if_completed(self):
        from .match import Match

        with transaction.atomic():
            # if there are no matches without results, this round is complete
            # if this round close attempt results in a row update, try to close the competition
            if (
                Match.objects.filter(round=self, result__isnull=True).count() == 0
                and Round.objects.filter(id=self.id, complete=False).update(complete=True, finished=timezone.now()) > 0
            ):
                self.competition.try_to_close()

    def get_absolute_url(self):
        return reverse("round", kwargs={"pk": self.pk})

    def as_html_link(self):
        return mark_safe(f'<a href="{self.get_absolute_url()}">{escape(self.__str__())}</a>')


@receiver(pre_save, sender=Round)
def pre_save_round(sender, instance, **kwargs):
    if instance.number is None:
        instance.number = Round.objects.filter(competition=instance.competition).count() + 1
