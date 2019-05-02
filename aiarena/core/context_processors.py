from datetime import datetime, timedelta

from aiarena.core.models import Match


def stats(request):
    matches_count = Match.objects.filter(created__gte=datetime.now() - timedelta(hours=24)).count()
    return {
        'matches_count': matches_count,
    }
