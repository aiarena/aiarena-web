from datetime import timedelta

from django.db.models import Prefetch
from django.utils.timezone import now
from django.views.generic import DetailView

from aiarena.core.models import Bot, MatchParticipation, Result, User


class AuthorDetail(DetailView):
    queryset = User.objects.filter(is_active=1, type="WEBSITE_USER").only(
        "username", "date_joined", "patreon_level", "last_login"
    )
    template_name = "author.html"
    context_object_name = "author"  # change the context name to avoid overriding the current user context object

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["bot_list"] = (
            Bot.objects.select_related("plays_race")
            .only("name", "type", "plays_race")
            .filter(user_id=self.object.id)
            .order_by("-created")
        )
        results_queryset = (
            Result.objects.filter(match__matchparticipation__bot__in=context["bot_list"])
            .filter(created__gt=now() - timedelta(days=30))
            .only("type", "match__requested_by__username", "created", "game_steps", "replay_file", "winner__name")
            .select_related("match__requested_by", "winner")
            .order_by("-created")
            .prefetch_related(
                Prefetch(
                    "match__matchparticipation_set",
                    MatchParticipation.objects.all()
                    .prefetch_related("bot")
                    .only("participant_number", "bot_id", "match_id", "elo_change"),
                    to_attr="participants",
                ),
            )[:25]
        )
        context["result_list"] = results_queryset
        return context
