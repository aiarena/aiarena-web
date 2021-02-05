import logging

from django.db import models

from .user import User
from .tag import Tag

logger = logging.getLogger(__name__)


class MatchTag(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    tag = models.ForeignKey(Tag, on_delete=models.CASCADE)

    def __str__(self):
        return f"{str(self.tag)} ({self.user.username})"
