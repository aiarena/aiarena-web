from datetime import timedelta

from django.db.models import Prefetch
from django.utils import timezone
from django.views.generic import DetailView

from aiarena.core.models import Match, MatchParticipation, Result, User


class ArenaClientView(DetailView):
    queryset = User.objects.filter(type="ARENA_CLIENT")
    template_name = "arenaclient.html"
    context_object_name = "arenaclient"  # change the context name to avoid overriding the current user oontext object

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        arenaclient = self.object
        results = self.get_results(arenaclient)

        context["assigned_matches_list"] = self.get_assigned_matches()
        context["ac_match_count_1h"] = self.get_match_count(hours=1)
        context["ac_match_count_24h"] = self.get_match_count(hours=24)
        context["ac_match_count"] = results.count()
        context["recent_result_list"] = results[:100]
        return context

    def get_assigned_matches(self):
        return (
            Match.objects.filter(assigned_to=self.object, result__isnull=True)
            .select_related("map")
            .only("map__name", "started")
            .prefetch_related(
                Prefetch(
                    "matchparticipation_set",
                    MatchParticipation.objects.all()
                    .select_related("bot")
                    .only("match_id", "participant_number", "bot__name"),
                    to_attr="participants",
                )
            )
        )

    def get_results(self, arenaclient):
        return (
            Result.objects.filter(match__assigned_to=arenaclient)
            .order_by("-created")
            .select_related("winner", "match")
            .only("type", "game_steps", "created", "match__id", "match__requested_by_id", "winner__name", "replay_file")
            .prefetch_related(
                Prefetch(
                    "match__matchparticipation_set",
                    MatchParticipation.objects.all()
                    .select_related("bot")
                    .only("participant_number", "elo_change", "match_id", "bot__name"),
                    to_attr="participants",
                ),
            )
        )

    def get_match_count(self, hours):
        time_threshold = timezone.now() - timedelta(hours=hours)
        return Result.objects.filter(match__assigned_to=self.object, created__gte=time_threshold).count()
