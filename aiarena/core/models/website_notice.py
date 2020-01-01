import logging

from django.db import models

from .user import User

logger = logging.getLogger(__name__)


class WebsiteNotice(models.Model):
    """ Represents a notice to be displayed on the website """
    title = models.CharField(max_length=20)
    description = models.TextField()
    created = models.DateTimeField(auto_now_add=True)
    display = models.BooleanField(default=True)
    posted_by = models.ForeignKey(User, on_delete=models.SET_NULL, blank=True, null=True)
