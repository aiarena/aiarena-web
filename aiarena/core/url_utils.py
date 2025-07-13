from django.urls import reverse


def get_bot_absolute_url(bot):
    """
    Returns the absolute URL for a bot.
    """
    return reverse("bot", kwargs={"pk": bot.pk})
