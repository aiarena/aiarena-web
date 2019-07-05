from django import template


def format_elo_change(value):
    """Custom formatting for ELO change integers"""
    if value is None:
        return ""
    elif value == 0:
        return "--"
    else:
        return "%+d" % value


register = template.Library()
register.filter('format_elo_change', format_elo_change)
