from django.db.models import Prefetch
from django.views.generic import DetailView

from aiarena.core.models import Match, MatchParticipation, Round


class RoundDetail(DetailView):
    model = Round
    template_name = "round.html"

    def get_queryset(self):
        qs = super().get_queryset()
        return qs.prefetch_related(
            Prefetch(
                "match_set",
                queryset=Match.objects.select_related("result", "assigned_to").prefetch_related(
                    Prefetch(
                        "matchparticipation_set",
                        queryset=MatchParticipation.objects.filter(participant_number=1).select_related("bot"),
                        to_attr="_participant1_list",
                    ),
                    Prefetch(
                        "matchparticipation_set",
                        queryset=MatchParticipation.objects.filter(participant_number=2).select_related("bot"),
                        to_attr="_participant2_list",
                    ),
                ),
            )
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        matches_finished = 0
        matches_started = 0
        matches_queued = 0

        matches = self.object.match_set.all()
        for match in matches:
            if match.status == "Finished":
                matches_finished += 1
            elif match.status == "Started":
                matches_started += 1
            elif match.status == "Queued":
                matches_queued += 1
            else:
                raise "A match had an unknown status!"

        context["matches_finished"] = matches_finished
        context["matches_started"] = matches_started
        context["matches_queued"] = matches_queued

        return context
