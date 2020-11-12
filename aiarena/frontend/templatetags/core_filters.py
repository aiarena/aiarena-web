from django import template


def cents_to_usd(cents):
    if cents is None:
        return "--"
    return str(float(cents / 100)) + '$'


def format_elo_change(value):
    """Custom formatting for ELO change integers"""
    if value is None or value == 0:
        return "--"
    else:
        return "%+d" % value


def smooth_timedelta(timedeltaobj):
    """Convert a datetime.timedelta object into Days, Hours, Minutes, Seconds."""
    secs = timedeltaobj.total_seconds()
    timetot = ""
    if secs > 86400:  # 60sec * 60min * 24hrs
        days = secs // 86400
        timetot += "{} days".format(int(days))
        secs = secs - days * 86400

    if secs > 3600:
        hrs = secs // 3600
        timetot += " {} hours".format(int(hrs))
        secs = secs - hrs * 3600

    if secs > 60:
        mins = secs // 60
        timetot += " {} minutes".format(int(mins))
        secs = secs - mins * 60

    if secs > 0:
        timetot += " {} seconds".format(int(secs))
    return timetot


register = template.Library()
register.filter('format_elo_change', format_elo_change)
register.filter('smooth_timedelta', smooth_timedelta)
register.filter('cents_to_usd', cents_to_usd)
