from datetime import timedelta

from constance import config
from django.utils import timezone

from aiarena import settings
from aiarena.core.models import Bot, Result, User, Season


# these are available globally in the django templates
def stats(request):
    return {
        'match_count_1h': Result.objects.only('id').filter(created__gte=timezone.now() - timedelta(hours=1)).count(),
        'match_count_24h': Result.objects.only('id').filter(created__gte=timezone.now() - timedelta(hours=24)).count(),
        'active_bots': Bot.objects.only('id').filter(active=True).count(),
        'arenaclients': User.objects.only('id').filter(type='ARENA_CLIENT', is_active=True).count(),
        'aiarena_settings': settings,
        'random_donator': User.random_donator(),
        'config': config,
        'current_season': Season.get_current_season_or_none(),
    }
