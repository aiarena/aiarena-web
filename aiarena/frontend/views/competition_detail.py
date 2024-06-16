from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator
from django.db import connection
from django.db.models import Prefetch
from django.views.generic import DetailView

from constance import config

from aiarena.core.models import Bot, Competition, CompetitionParticipation, RelativeResult, Round, User
from aiarena.core.services import Ladders
from aiarena.frontend.utils import restrict_page_range


class CompetitionDetail(DetailView):
    model = Competition
    template_name = "competition.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        maps = self.object.maps.all()
        map_names = []
        for map in maps:
            map_names.append(map.name)
        context["map_names"] = map_names

        elo_trend_n_matches = config.ELO_TREND_N_MATCHES

        rounds = Round.objects.filter(competition_id=self.object.id).order_by("-id")
        page = self.request.GET.get("page", 1)
        paginator = Paginator(rounds, 30)
        try:
            rounds = paginator.page(page)
        except PageNotAnInteger:
            rounds = paginator.page(1)
        except EmptyPage:
            rounds = paginator.page(paginator.num_pages)
        context["round_list"] = rounds
        context["round_page_range"] = restrict_page_range(paginator.num_pages, rounds.number)

        if self.object.status == "closed":
            all_participants = Ladders.get_competition_last_round_participants(self.object)
        else:
            all_participants = Ladders.get_competition_ranked_participants(self.object, include_placements=True)
        all_participants = list(
            all_participants.prefetch_related(
                Prefetch(
                    "bot",
                    queryset=Bot.objects.all()
                    .select_related("plays_race")
                    .only("plays_race", "user_id", "name", "type", "plays_race"),
                ),
                Prefetch("bot__user", queryset=User.objects.all().only("patreon_level", "username", "type")),
            )
        )

        relative_result = RelativeResult.with_row_number([x.bot.id for x in all_participants], self.object)

        # This check avoids a potential EmptyResultSet exception.
        # See https://code.djangoproject.com/ticket/26061
        if relative_result.count() > 0:
            sql, params = relative_result.query.sql_with_params()

            with connection.cursor() as cursor:
                cursor.execute(
                    """
                    SELECT bot_id as id, SUM("elo_change") trend FROM ({}) row_numbers
                    WHERE "row_number" <= %s
                    GROUP BY bot_id
                """.format(
                        sql
                    ),
                    [*params, elo_trend_n_matches],
                )
                rows = cursor.fetchall()
                for participant in all_participants:
                    participant.trend = next(iter([x[1] for x in rows if x[0] == participant.bot.id]), None)

        context["divisions"] = dict()
        to_title = lambda x: "Awaiting Entry" if x == CompetitionParticipation.DEFAULT_DIVISION else f"Division {x}"
        for participant in all_participants:
            if to_title(participant.division_num) not in context["divisions"]:
                context["divisions"][to_title(participant.division_num)] = []
            context["divisions"][to_title(participant.division_num)].append(participant)
        return context
