import json

from django.views.generic import DetailView

from aiarena.core.models import CompetitionParticipation
from aiarena.core.services.service_implementations.internal.statistics.elo_graphs_generator import EloGraphsGenerator


class BotCompetitionStatsDetail(DetailView):
    model = CompetitionParticipation
    template_name = "bot_competition_stats.html"
    queryset = CompetitionParticipation.objects.select_related("competition", "bot")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        competition = context["competitionparticipation"].competition
        context["competition_bot_matchups"] = self.__get_competition_bot_matchups(competition)
        context["competition_map_stats"] = self.__get_competition_map_stats()
        context["updated"] = (
            context["competition_bot_matchups"][0].updated if context["competition_bot_matchups"] else "Never"
        )
        context["competition_closed"] = competition.statistics_finalized

        if not context["competition_closed"]:
            context["elo_chart_data"] = self.__get_elo_chart_data(context["competitionparticipation"], competition.id)
            context["winrate_chart_data"] = self.__get_winrate_chart_data(
                context["competitionparticipation"], competition.id
            )

        return context

    def __get_elo_chart_data(self, sp, competition_id):
        elo_data = EloGraphsGenerator(sp)._get_elo_data(self.object.bot, competition_id)
        last_updated = (
            EloGraphsGenerator(sp)._get_graph_update_line_datetime(self.object.bot, competition_id).timestamp() * 1000
            if sp.bot.user == self.request.user and self.request.user.patreon_level != "none"
            else None
        )

        return json.dumps(
            {
                "title": "ELO over time",
                "lastUpdated": last_updated,
                "data": {
                    "datasets": [
                        {
                            "label": "ELO",
                            "backgroundColor": "#86c232",
                            "borderColor": "#86c232",
                            "data": [{"x": elo[2].timestamp() * 1000, "y": elo[1]} for elo in elo_data],
                        }
                    ],
                },
            },
            default=str,
        )

    def __get_winrate_chart_data(self, sp, competition_id):
        winrate_data = EloGraphsGenerator(sp)._get_winrate_data(self.object.bot.id, competition_id)
        winrate_data_with_total = [(x[0], x[1], x[2], x[3], x[4], (x[1] + x[2] + x[3] + x[4])) for x in winrate_data]
        labels = [f"{winrate[0]}-{winrate[0] + 5}" for winrate in winrate_data_with_total]
        if len(labels) > 0:
            if labels[-1] == "30-35":
                labels[-1] = "30+"
        datasets = []
        # Wins
        datasets.append(
            {
                "label": "Wins",
                "data": [x[1] for x in winrate_data_with_total],
                "backgroundColor": "#86C232",
                "extraLabels": [str(round((x[1] / x[5] if x[5] else 0) * 100)) + "%" for x in winrate_data_with_total],
                "datalabels": {"align": "center", "anchor": "center"},
            }
        )

        # Losses
        datasets.append(
            {
                "label": "Losses",
                "data": [x[2] for x in winrate_data_with_total],
                "backgroundColor": "#D20044",
                "extraLabels": [str(round((x[2] / x[5] if x[5] else 0) * 100)) + "%" for x in winrate_data_with_total],
                "datalabels": {"align": "center", "anchor": "center"},
            }
        )

        # Crashes
        datasets.append(
            {
                "label": "Crashes",
                "data": [x[3] for x in winrate_data_with_total],
                "backgroundColor": "#AAAAAA",
                "extraLabels": [str(round((x[3] / x[5] if x[5] else 0) * 100)) + "%" for x in winrate_data_with_total],
                "datalabels": {"align": "center", "anchor": "center"},
            }
        )

        # Ties
        datasets.append(
            {
                "label": "Ties",
                "data": [x[4] for x in winrate_data_with_total],
                "backgroundColor": "#DFCE00",
                "extraLabels": [str(round((x[4] / x[5] if x[5] else 0) * 100)) + "%" for x in winrate_data_with_total],
                "datalabels": {"align": "center", "anchor": "center"},
            }
        )

        return json.dumps(
            {
                "title": "Result vs Match Duration",
                "data": {"labels": labels, "datasets": datasets},
            },
            default=str,
        )

    def __get_competition_map_stats(self):
        return self.object.competition_map_stats.select_related("map").order_by("map__name")

    def __get_competition_bot_matchups(self, competition):
        return (
            self.object.competition_matchup_stats.filter(opponent__competition=competition)
            .order_by("-win_perc")
            .distinct()
            .select_related("opponent__bot", "opponent__bot__plays_race")
        )
