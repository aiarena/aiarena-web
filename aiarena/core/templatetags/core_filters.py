from django import template

def with_symbol(value):
    """Formats an integer so as to include the positive or negative symbol"""
    return "%+d" % value

register = template.Library()
register.filter('with_symbol', with_symbol)
