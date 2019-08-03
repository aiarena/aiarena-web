from datetime import timedelta

from django.utils import timezone

from aiarena import settings
from aiarena.core.models import Bot, Result


# these are available globally in the django templates
def stats(request):
    return {
        'match_count_1h': Result.objects.filter(created__gte=timezone.now() - timedelta(hours=1)).count(),
        'match_count_24h': Result.objects.filter(created__gte=timezone.now() - timedelta(hours=24)).count(),
        'active_bots': Bot.objects.filter(active=True).count(),
        'aiarena_settings': settings,
    }
