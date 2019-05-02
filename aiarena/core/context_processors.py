from datetime import datetime, timedelta

from aiarena.core.models import Match, Bot


def stats(request):
    return {
        'matches_count': Match.objects.filter(created__gte=datetime.now() - timedelta(hours=24)).count(),
        'active_bots': Bot.objects.filter(active=True).count(),
    }
