from django import template


def pretty_bool(value):
    """
    -   filter for printing the ``Boolean`` values nicely

    :param value: True / False.
    :type str: string..

    :returns:  ``✔`` / ``✘``
    :raises: AttributeError, KeyError

        """
    if value == True:
        value = '✔'
        return value
    if value == False:
        value = '✘'
        return value
    if str(value).lower() == 'yes':
        value = '✔'
        return value
    if str(value).lower() == 'no':
        value = '✘'
        return value
    return value


def cents_to_usd(cents):
    if cents is None:
        return "--"
    return str(float(cents / 100)) + '$'


def format_elo_change(value):
    """Custom formatting for ELO change integers"""
    if value is None or value == 0:
        return "0"
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

def result_color_class(value):
    return f"result-{str(value).lower()}"

def step_time_color(value):
    """Generate color for given step time(ms)."""

    def get_color(w1, c1, c2):  # Gradient between c1 and c2
        w1 = 0 if w1 <= 0 else 1 if w1 >= 1 else w1
        w2 = 1 - w1
        rgb = [hex(round(c1[i] * w1 + c2[i] * w2))[2:] for i in range(3)]
        return [("0" + h) if len(h) < 2 else h for h in rgb]  # make sure always 2 chars long

    high_color = (255, 0, 0)  # Red
    mid_color = (255, 255, 0)  # Yellow
    low_color = (0, 255, 0)  # Green

    rgb = ["ff", "ff", "ff"]  # Default White
    minpoint = 10  # Step times
    midpoint = 30
    maxpoint = 50
    if isinstance(value, int):
        if value > midpoint:
            weight = (value - midpoint) / (maxpoint - midpoint)
            rgb = get_color(weight, high_color, mid_color)
        elif value <= midpoint:
            weight = (value - minpoint) / (midpoint - minpoint)
            rgb = get_color(weight, mid_color, low_color)
    return f"#{''.join(rgb)}"


def shorten_naturaltime(naturaltime):
    # Remove 0xa0 character separating words and replace with spaces
    naturaltime = " ".join(naturaltime.split())
    return (naturaltime
            .replace(' seconds', 's').replace(' second', 's')
            .replace(' minutes', 'm').replace('a minute', '1m')
            .replace(' hours', 'h').replace('an hour', '1h')
            .replace(' days', 'd').replace(' day', 'd')
            .replace(' months', 'mon').replace(' month', 'mon')
            .replace(' weeks', 'w').replace(' week', 'w')
            .replace(' years', 'y').replace(' year', 'y'))


def bot_competition_trend(bot, competition):
    return bot.current_elo_trend(competition)


register = template.Library()
register.filter('pretty_bool', pretty_bool)
register.filter('format_elo_change', format_elo_change)
register.filter('smooth_timedelta', smooth_timedelta)
register.filter('cents_to_usd', cents_to_usd)
register.filter('step_time_color', step_time_color)
register.filter('shorten_naturaltime', shorten_naturaltime)
register.simple_tag(bot_competition_trend, name='bot_competition_trend')
