from datetime import timedelta

from django.db.models import Count, Q
from django.utils import timezone
from django.views.generic import ListView

from aiarena.core.models import ArenaClient


class ArenaClients(ListView):
    template_name = "arenaclients.html"

    def get_queryset(self):
        now = timezone.now()
        one_hour_ago = now - timedelta(hours=1)
        twenty_four_hours_ago = now - timedelta(hours=24)

        return (
            ArenaClient.objects.select_related("owner")
            .filter(is_active=True)
            .annotate(matches_1hr=Count("submitted_results", filter=Q(submitted_results__created__gte=one_hour_ago)))
            .annotate(
                matches_24hr=Count("submitted_results", filter=Q(submitted_results__created__gte=twenty_four_hours_ago))
            )
        )
