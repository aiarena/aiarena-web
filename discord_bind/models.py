from django.conf import settings
from django.db import models

class DiscordUser(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="discord_user")
    discord_id = models.CharField(max_length=64, unique=True)
    username = models.CharField(max_length=128, blank=True, default="")

class DiscordInvite(models.Model):
    code = models.CharField(max_length=64, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
