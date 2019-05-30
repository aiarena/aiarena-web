from django import template


def with_symbol(value):
    """Formats an integer so as to include the positive or negative symbol"""
    if value is None:
        return ""
    else:
        return "%+d" % value


register = template.Library()
register.filter('with_symbol', with_symbol)
