from datetime import datetime, timedelta
from django.utils import timezone

from aiarena.core.models import Match, Bot


def stats(request):
    return {
        'match_count_1h': Match.objects.filter(created__gte=timezone.now() - timedelta(hours=1)).count(),
        'match_count_24h': Match.objects.filter(created__gte=timezone.now() - timedelta(hours=24)).count(),
        'active_bots': Bot.objects.filter(active=True).count(),
    }
