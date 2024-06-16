from django.db.models import F, Prefetch
from django.shortcuts import render
from django.views import View

from aiarena.core.models import Match, MatchParticipation, Round


class MatchQueue(View):
    def get(self, request):
        # Matches without a round are requested ones
        requested_matches = (
            Match.objects.filter(round__isnull=True, result__isnull=True)
            .order_by(F("started").asc(nulls_last=True), F("id").asc())
            .prefetch_related(
                Prefetch("map"),
                Prefetch(
                    "matchparticipation_set",
                    MatchParticipation.objects.all().prefetch_related("bot"),
                    to_attr="participants",
                ),
            )
        )

        # Matches with a round
        rounds = Round.objects.filter(complete=False).order_by(F("id").asc())
        for round in rounds:
            round.matches = (
                Match.objects.filter(round_id=round.id, result__isnull=True)
                .select_related("map")
                .order_by(F("started").asc(nulls_last=True), F("id").asc())
                .prefetch_related(
                    Prefetch(
                        "matchparticipation_set",
                        MatchParticipation.objects.all().prefetch_related("bot"),
                        to_attr="participants",
                    )
                )
            )

        context = {"round_list": rounds, "requested_matches": requested_matches}
        return render(request, "match_queue.html", context)
