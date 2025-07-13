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
def get_bot_truncated_html_link(bot) -> str:
    name = escape(bot.__str__())
    limit = 20
    return mark_safe(
        f'<a href="{get_absolute_url("bot", bot)}">{(name[:limit - 3] + "...") if len(name) > limit else name}</a>'
    )


def get_absolute_url(view_name, model_instance):
    """Returns the absolute URL for a model instance."""
    return reverse(view_name, kwargs={"pk": model_instance.pk})


valid_link_types = {
    "bot",
    "match",
    "author",  # for WebsiteUser
    "arenaclient",
    "round",
    "competition",
}


@register.simple_tag
def get_html_link(link_type: str, model_instance) -> str:
    """Returns an HTML link to a model instance."""
    url = get_absolute_url(link_type, model_instance)
    name = escape(str(model_instance))
    return mark_safe(f'<a href="{url}">{name}</a>')
