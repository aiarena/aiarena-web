import logging

from django.db import models
from django.db.models.signals import post_delete
from django.dispatch import receiver

from .tag import Tag
from .user import User


logger = logging.getLogger(__name__)


class MatchTag(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    tag = models.ForeignKey(Tag, on_delete=models.CASCADE)

    def __str__(self):
        return f"{str(self.tag)} ({self.user.username})"


@receiver(post_delete, sender=MatchTag)
def delete_orphan_tags(sender, instance, **kwargs):
    # If there are no objects that refer to this tag left, delete the tag
    if not sender.objects.filter(tag=instance.tag):
        instance.tag.delete()
