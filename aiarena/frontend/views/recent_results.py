from django.db.models import Prefetch
from django.views.generic import ListView

from aiarena.core.models import MatchParticipation, Result


class RecentResults(ListView):
    queryset = (
        Result.objects.all()
        .order_by("-created")
        .prefetch_related(
            Prefetch("winner"),
            Prefetch("match__requested_by"),
            Prefetch(
                "match__matchparticipation_set",
                MatchParticipation.objects.all().prefetch_related("bot"),
                to_attr="participants",
            ),
        )[:200]
    )
    template_name = "recent_results.html"
