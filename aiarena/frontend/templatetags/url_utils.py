from django import template
from django.urls import reverse
from django.utils.html import escape
from django.utils.safestring import mark_safe


register = template.Library()


def get_bot_absolute_url(bot) -> str:
    """
    Returns the absolute URL for a bot.
    """
    return reverse("bot", kwargs={"pk": bot.pk})


@register.simple_tag
def get_bot_html_link(bot) -> str:
    """
    Returns an HTML link to the bot.
    """
    return mark_safe(f'<a href="{get_bot_absolute_url(bot)}">{escape(str(bot))}</a>')


@register.simple_tag
def get_bot_truncated_html_link(bot) -> str:
    name = escape(bot.__str__())
    limit = 20
    return mark_safe(
        f'<a href="{get_bot_absolute_url(bot)}">{(name[:limit-3] + "...") if len(name) > limit else name}</a>'
    )
