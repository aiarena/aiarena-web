# =============================================================================
# If there are any changes made to this file, run the following in the
# development environment to generate a new schema:
#
#     python manage.py graphql_schema
#
# =============================================================================
from datetime import timedelta
from decimal import ROUND_CEILING, ROUND_FLOOR, Decimal

from django.conf import settings
from django.db.models import CharField, Count, IntegerField, OuterRef, Prefetch, Q, Subquery
from django.db.models.functions import Lower
from django.utils import timezone

import django_filters
import graphene
from avatar.models import Avatar
from django_filters import FilterSet, OrderingFilter
from graphene_django import DjangoConnectionField
from graphene_django.filter import DjangoFilterConnectionField
from graphql_relay import from_global_id
from rest_framework.authtoken.models import Token

from aiarena.core import models
from aiarena.core.models import BotRace, Match, MatchParticipation, Result, User
from aiarena.core.models.result import STEPS_PER_SECOND
from aiarena.core.services import ladders, match_requests, supporters, users
from aiarena.core.services.service_implementations.internal.statistics.elo_graphs_generator import EloGraphsGenerator
from aiarena.frontend.templatetags.url_utils import get_absolute_url
from aiarena.frontend.views.bot_detail import RelativeResultFilter
from aiarena.graphql.chart_types import EloChartType, RaceMatchupBreakdownType, WinrateChartType
from aiarena.graphql.common import CountingConnection, DjangoObjectTypeWithUID


class BotRaceType(DjangoObjectTypeWithUID):
    name = graphene.String()

    class Meta:
        model = models.BotRace
        fields = [
            "id",
            "label",
            "name",
        ]
        filter_fields = []
        connection_class = CountingConnection

    @staticmethod
    def resolve_name(root: BotRace, info, **args):
        return root.get_label_display()


class BotFilterSet(FilterSet):
    order_by = OrderingFilter(
        fields=[
            "name",
            "user__username",
            "plays_race",
            "type",
            "created",
            "bot_zip_updated",
            "total_active_competition_participations",
        ],
        method="filter_order_by",
    )
    user_id = graphene.ID()
    name = django_filters.CharFilter(method="filter_name")
    bot_zip_publicly_downloadable = django_filters.BooleanFilter()

    class Meta:
        model = models.Bot
        fields = [
            "name",
            "user_id",
            "order_by",
            "bot_zip_publicly_downloadable",
        ]

    def filter_name(self, queryset, name, value):
        # Search by both bot name and author username
        return queryset.filter(Q(name__icontains=value) | Q(user__username__icontains=value))

    def filter_order_by(self, queryset, name, value):
        order_fields = value if isinstance(value, list) else [value]

        if any("total_active_competition_participations" in f for f in order_fields):
            queryset = queryset.annotate(
                total_active_competition_participations=Count(
                    "competition_participations",
                    filter=Q(competition_participations__active=True),
                )
            )

        return queryset.order_by(*order_fields)


class BotType(DjangoObjectTypeWithUID):
    url = graphene.String()
    competition_participations = DjangoFilterConnectionField("aiarena.graphql.CompetitionParticipationType")
    wiki_article = graphene.String()
    match_participations = DjangoFilterConnectionField("aiarena.graphql.MatchParticipationType")
    trophies = DjangoConnectionField("aiarena.graphql.TrophyType")

    class Meta:
        model = models.Bot
        fields = [
            "user",
            "name",
            "created",
            "bot_zip",
            "bot_zip_updated",
            "bot_zip_publicly_downloadable",
            "bot_data_enabled",
            "bot_data",
            "bot_data_publicly_downloadable",
            "type",
            "plays_race",
        ]
        filterset_class = BotFilterSet
        connection_class = CountingConnection

    @staticmethod
    def resolve_url(root: models.Bot, info, **args):
        return get_absolute_url("bot", root)

    @staticmethod
    def resolve_competition_participations(root: models.Bot, info, **args):
        return root.competition_participations.order_by("-competition__date_created")

    @staticmethod
    def resolve_wiki_article(root: models.Bot, info, **args):
        return root.get_wiki_article().current_revision.content

    @staticmethod
    def resolve_match_participations(root: models.Bot, info, **args):
        return root.matchparticipation_set.all()


class CompetitionFilterSet(FilterSet):
    order_by = OrderingFilter(
        fields=[
            "id",
            "name",
            "date_created",
            "date_opened",
            "date_closed",
        ],
        method="filter_order_by",
    )
    competition_id = graphene.ID()
    name = django_filters.CharFilter(method="filter_name")

    class Meta:
        model = models.Competition
        fields = ["name", "id", "order_by", "status"]

    def filter_name(self, queryset, name, value):
        return queryset.filter(Q(name__icontains=value))

    def filter_order_by(self, queryset, name, value):
        order_fields = value if isinstance(value, list) else [value]

        return queryset.order_by(*order_fields)


class CompetitionType(DjangoObjectTypeWithUID):
    url = graphene.String()
    participants = DjangoConnectionField("aiarena.graphql.CompetitionParticipationType")
    rounds = DjangoConnectionField("aiarena.graphql.RoundsType")
    maps = DjangoConnectionField("aiarena.graphql.MapType")
    game = graphene.String()
    game_mode = graphene.String()
    wiki_article = graphene.String()

    class Meta:
        model = models.Competition
        fields = [
            "name",
            "date_created",
            "date_opened",
            "date_closed",
            "status",
        ]
        filterset_class = CompetitionFilterSet
        connection_class = CountingConnection

    @staticmethod
    def resolve_rounds(root: models.Competition, info, **args):
        return root.round_set.all().order_by("-started")

    @staticmethod
    def resolve_game(root: models.Competition, info, **args):
        return root.game_mode.game

    @staticmethod
    def resolve_game_mode(root: models.Competition, info, **args):
        return root.game_mode

    @staticmethod
    def resolve_url(root: models.Competition, info, **args):
        return get_absolute_url("competition", root)

    @staticmethod
    def resolve_participants(root: models.Competition, info, **args):
        return ladders.get_competition_display_full_rankings(root).calculate_trend(root)

    @staticmethod
    def resolve_wiki_article(root: models.Bot, info, **args):
        return root.get_wiki_article().current_revision.content


class CompetitionBotMapStatsFilterSet(FilterSet):
    order_by = OrderingFilter(
        fields=[
            "map__name",
            "match_count",
            "win_count",
            "win_perc",
            "loss_count",
            "loss_perc",
            "tie_count",
            "tie_perc",
            "crash_count",
            "crash_perc",
        ],
    )

    class Meta:
        model = models.CompetitionBotMapStats
        fields = ["order_by"]


class CompetitionBotMapStatsType(DjangoObjectTypeWithUID):
    class Meta:
        model = models.CompetitionBotMapStats
        fields = [
            "map",
            "match_count",
            "win_count",
            "win_perc",
            "loss_count",
            "loss_perc",
            "tie_count",
            "tie_perc",
            "crash_count",
            "crash_perc",
            "updated",
        ]
        filterset_class = CompetitionBotMapStatsFilterSet
        connection_class = CountingConnection


class CompetitionBotMatchupStatsFilterSet(FilterSet):
    order_by = OrderingFilter(
        fields=[
            "opponent__bot__name",
            "opponent__bot__plays_race__label",
            "match_count",
            "win_count",
            "win_perc",
            "loss_count",
            "loss_perc",
            "tie_count",
            "tie_perc",
            "crash_count",
            "crash_perc",
        ],
    )

    class Meta:
        model = models.CompetitionBotMatchupStats
        fields = ["order_by"]


class CompetitionBotMatchupStatsType(DjangoObjectTypeWithUID):
    class Meta:
        model = models.CompetitionBotMatchupStats
        fields = [
            "opponent",
            "match_count",
            "win_count",
            "win_perc",
            "loss_count",
            "loss_perc",
            "tie_count",
            "tie_perc",
            "crash_count",
            "crash_perc",
            "updated",
        ]
        filterset_class = CompetitionBotMatchupStatsFilterSet
        connection_class = CountingConnection


class CompetitionParticipationFilterSet(FilterSet):
    order_by = OrderingFilter(
        fields=[
            "competition__date_opened",
        ],
        method="filter_order_by",
    )

    active = django_filters.BooleanFilter()
    name = django_filters.CharFilter(method="filter_name")

    class Meta:
        model = models.CompetitionParticipation
        fields = [
            "order_by",
            "active",
        ]

    def filter_order_by(self, queryset, name, value):
        order_fields = value if isinstance(value, list) else [value]
        return queryset.order_by(*order_fields)


class CompetitionParticipationType(DjangoObjectTypeWithUID):
    trend = graphene.Int()
    competition_map_stats = DjangoFilterConnectionField(
        "aiarena.graphql.CompetitionBotMapStatsType", filterset_class=CompetitionBotMapStatsFilterSet
    )
    competition_matchup_stats = DjangoFilterConnectionField(
        "aiarena.graphql.CompetitionBotMatchupStatsType", filterset_class=CompetitionBotMatchupStatsFilterSet
    )

    elo_chart_data = graphene.Field(EloChartType)
    winrate_chart_data = graphene.Field(WinrateChartType)
    race_matchup = graphene.Field(RaceMatchupBreakdownType)

    class Meta:
        model = models.CompetitionParticipation
        fields = [
            "competition",
            "match_count",
            "win_perc",
            "win_count",
            "loss_perc",
            "loss_count",
            "tie_perc",
            "tie_count",
            "crash_perc",
            "crash_count",
            "highest_elo",
            "elo",
            "division_num",
            "bot",
            "active",
        ]
        filterset_class = CompetitionParticipationFilterSet
        connection_class = CountingConnection

    @staticmethod
    def resolve_trend(root: models.CompetitionParticipation, info, **args):
        if hasattr(root, "trend"):
            return root.trend
        trend_data = models.CompetitionParticipation.objects.filter(id=root.id).calculate_trend(root.competition)
        if trend_data:
            return trend_data[0].trend
        return 0

    @staticmethod
    def resolve_competition_map_stats(root: models.CompetitionParticipation, info, **args):
        return root.competition_map_stats.select_related("map").order_by("map__name")

    @staticmethod
    def resolve_competition_matchup_stats(root: models.CompetitionParticipation, info, **args):
        return (
            root.competition_matchup_stats.filter(opponent__competition=root.competition)
            .order_by("-win_perc")
            .distinct()
            .select_related("opponent__bot", "opponent__bot__plays_race")
        )

    @staticmethod
    def resolve_elo_chart_data(root, info, **args):
        competition = root.competition
        if competition.statistics_finalized:
            return None

        gen = EloGraphsGenerator(root)
        elo_data = gen._get_elo_data(root.bot, competition.id)

        if not elo_data:
            last_updated = None
            datasets = []

        else:
            xs_ms = [e[2].timestamp() * 1000 for e in elo_data]
            min_x, max_x = min(xs_ms), max(xs_ms)

            dt = gen._get_graph_update_line_datetime(root.bot, competition.id)
            candidate_last_updated = dt.timestamp() * 1000 if dt else None

            if candidate_last_updated is not None and min_x <= candidate_last_updated <= max_x:
                last_updated = candidate_last_updated
            else:
                last_updated = None

            datasets = [
                {
                    "label": "ELO",
                    "backgroundColor": "#86c232",
                    "borderColor": "#86c232",
                    "data": [{"x": x, "y": e[1]} for x, e in zip(xs_ms, elo_data)],
                }
            ]

        return {
            "title": "ELO over time",
            "lastUpdated": last_updated,
            "data": {"datasets": datasets},
        }

    @staticmethod
    def resolve_winrate_chart_data(root, info, **args):
        competition = root.competition
        if competition.statistics_finalized:
            return None

        gen = EloGraphsGenerator(root)
        data = gen._get_winrate_data(root.bot.id, competition.id)

        with_total = [(d, w, l, c, t, (w + l + c + t)) for d, w, l, c, t in data]

        labels = [f"{x[0]}-{x[0] + 5}" for x in with_total]
        if labels and labels[-1] == "30-35":
            labels[-1] = "30+"

        def pct(p, total):
            return f"{round((p / total if total else 0) * 100)}%"

        def ds(label, idx, color):
            return {
                "label": label,
                "data": [x[idx] for x in with_total],
                "backgroundColor": color,
                "extraLabels": [pct(x[idx], x[5]) for x in with_total],
                "datalabels": {"align": "center", "anchor": "center"},
            }

        return {
            "title": "Result vs Match Duration",
            "data": {
                "labels": labels,
                "datasets": [
                    ds("Wins", 1, "#86C232"),
                    ds("Losses", 2, "#D20044"),
                    ds("Ties", 4, "#DFCE00"),
                    ds("Crashes", 3, "#AAAAAA"),
                ],
            },
        }

    @staticmethod
    def resolve_race_matchup(root, info, **args):
        request = info.context
        user = getattr(request, "user", None)
        # Wins by race is only  available for Patreon users
        if user and user.is_authenticated:
            if user.is_superuser or (root.bot.user == user and getattr(user, "patreon_level", "none") != "none"):
                competition = root.competition
                if competition.statistics_finalized:
                    return None

                gen = EloGraphsGenerator(root)
                rows = gen._get_race_outcome_breakdown_data(root.bot.id, competition.id)
                breakdown = gen._race_outcome_breakdown(rows)

                def normalize(d):
                    return {
                        "wins": d.get("wins", 0),
                        "losses": d.get("losses", 0),
                        "ties": d.get("ties", 0),
                        "crashes": d.get("crashes", 0),
                        "played": d.get("played", 0),
                        "winRate": d.get("winRate", 0.0),
                        "lossRate": d.get("lossRate", 0.0),
                        "tieRate": d.get("tieRate", 0.0),
                        "crashRate": d.get("crashRate", 0.0),
                    }

                return {
                    "zerg": normalize(breakdown.get("Z", {})),
                    "protoss": normalize(breakdown.get("P", {})),
                    "terran": normalize(breakdown.get("T", {})),
                    "random": normalize(breakdown.get("R", {})),
                }


class MatchParticipationFilterSet(FilterSet):
    order_by = OrderingFilter(
        fields=[
            "id",
        ],
        method="filter_order_by",
    )
    opponent_id = django_filters.CharFilter(method="filter_opponent_id")
    opponent_plays_race = django_filters.ChoiceFilter(
        field_name="plays_race",
        method="filter_opponent_plays_race",
        choices=models.Bot.RACES,
    )

    result = django_filters.ChoiceFilter(field_name="result", choices=models.MatchParticipation.RESULT_TYPES)
    cause = django_filters.ChoiceFilter(field_name="result_cause", choices=models.MatchParticipation.CAUSE_TYPES)

    avg_step_time_min = django_filters.NumberFilter(method="filter_avg_step_time_min")
    avg_step_time_max = django_filters.NumberFilter(method="filter_avg_step_time_max")

    game_time_min = django_filters.NumberFilter(method="filter_game_time_min")
    game_time_max = django_filters.NumberFilter(method="filter_game_time_max")

    match_type = django_filters.ChoiceFilter(
        choices=RelativeResultFilter.MATCH_TYPES,
        method="filter_match_type",
    )
    map_name = django_filters.CharFilter(field_name="match__map__name", lookup_expr="icontains")
    competition_id = django_filters.CharFilter(method="filter_competition")

    match_started_after = django_filters.DateTimeFilter(field_name="match__started", lookup_expr="gte")
    match_started_before = django_filters.DateTimeFilter(field_name="match__started", lookup_expr="lte")

    class Meta:
        model = models.MatchParticipation
        fields = [
            "order_by",
            "result",
            "cause",
            "avg_step_time_min",
            "avg_step_time_max",
            "game_time_min",
            "game_time_max",
            "map_name",
            "competition_id",
            "opponent_plays_race",
            "match_started_after",
            "match_started_before",
        ]

    def filter_order_by(self, queryset, name, value):
        order_fields = value if isinstance(value, list) else [value]
        return queryset.order_by(*order_fields)

    @property
    def qs(self):
        qs = super().qs

        qs = qs.select_related(
            "bot",
            "match",
            "match__map",
            "match__round",
            "match__round__competition",
            "match__result",
        )

        qs = qs.prefetch_related(
            Prefetch(
                "match__matchparticipation_set",
                queryset=models.MatchParticipation.objects.select_related("bot"),
            )
        )

        return qs

    def _with_opponent_annotation(self, queryset):
        opponent_qs = models.MatchParticipation.objects.filter(match=OuterRef("match_id")).exclude(pk=OuterRef("pk"))

        return queryset.annotate(
            opponent_name=Subquery(
                opponent_qs.annotate(lower_name=Lower("bot__name")).values("lower_name")[:1],
                output_field=CharField(),
            ),
            opponent_plays_race=Subquery(opponent_qs.values("bot__plays_race")[:1]),
            opponent_id=Subquery(
                opponent_qs.values("bot__id")[:1],
                output_field=IntegerField(),
            ),
        )

    def filter_opponent_id(self, queryset, name, value):
        if not value:
            return queryset
        try:
            _type, db_id = from_global_id(value)
            value = db_id
        except Exception:
            pass
        try:
            value = int(value)
        except (TypeError, ValueError):
            return queryset.none()

        qs = self._with_opponent_annotation(queryset)
        return qs.filter(opponent_id=value)

    def filter_opponent_name(self, queryset, name, value):
        if not value:
            return queryset

        qs = self._with_opponent_annotation(queryset)
        return qs.filter(opponent_name__icontains=value)

    def filter_opponent_plays_race(self, queryset, name, value):
        if not value:
            return queryset

        qs = self._with_opponent_annotation(queryset)
        race_id = BotRace.objects.get(label=value)
        return qs.filter(opponent_plays_race=race_id)

    def filter_competition(self, queryset, name, value):
        _type, db_id = from_global_id(value)
        return queryset.filter(match__round__competition_id=db_id)

    def filter_avg_step_time_min(self, queryset, name, value):
        if value is None:
            return queryset

        seconds = value / Decimal("1000")
        return queryset.filter(avg_step_time__gte=seconds)

    def filter_avg_step_time_max(self, queryset, name, value):
        if value is None:
            return queryset

        seconds = value / Decimal("1000")
        return queryset.filter(avg_step_time__lte=seconds)

    def filter_game_time_min(self, queryset, name, value):
        if value is None:
            return queryset

        sec = Decimal(value)
        steps_dec = sec * Decimal(STEPS_PER_SECOND)
        steps_min = steps_dec.to_integral_value(rounding=ROUND_CEILING)

        return queryset.filter(match__result__game_steps__gte=int(steps_min))

    def filter_game_time_max(self, queryset, name, value):
        if value is None:
            return queryset

        sec = Decimal(value)
        steps_dec = sec * Decimal(STEPS_PER_SECOND)
        steps_max = steps_dec.to_integral_value(rounding=ROUND_FLOOR)

        return queryset.filter(match__result__game_steps__lte=int(steps_max))

    def filter_match_type(self, queryset, name, value):
        if not value:
            return queryset

        if value == "requested":
            return queryset.filter(match__requested_by__isnull=False)

        if value == "competition":
            return queryset.filter(match__round__isnull=False)

        return queryset


class MatchParticipationType(DjangoObjectTypeWithUID):
    match_log = graphene.String()

    class Meta:
        model = models.MatchParticipation
        fields = ["elo_change", "avg_step_time", "result", "bot", "match", "result_cause"]
        filterset_class = MatchParticipationFilterSet
        connection_class = CountingConnection

    def resolve_opponent_plays_race_enum(self, info):
        return self.opponent_plays_race

    def resolve_match_log(self, info):
        if not self.match_log:
            return ""

        user = getattr(info.context, "user", None)
        if user and self.can_download_match_log(user):
            return str(self.match_log)

        return ""


class MatchFilterSet(FilterSet):
    order_by = OrderingFilter(
        fields=[
            "id",
            "participant1__bot__name",
            "participant2__bot__name",
            "result__type",
            "map__name",
            "started",
            "tags",
        ],
        method="filter_order_by",
    )

    class Meta:
        model = models.Match
        fields = ["order_by"]

    def filter_order_by(self, queryset, name, value):
        order_fields = value if isinstance(value, list) else [value]
        if any("participant1__bot__name" in f for f in order_fields):
            subquery = (
                MatchParticipation.objects.filter(match=OuterRef("pk"), participant_number=1)
                .annotate(lower_name=Lower("bot__name"))
                .values("lower_name")[:1]
            )
            queryset = queryset.annotate(participant1_name=Subquery(subquery, output_field=CharField()))
            order_fields = [f.replace("participant1__bot__name", "participant1_name") for f in order_fields]

        if any("participant2__bot__name" in f for f in order_fields):
            subquery = (
                MatchParticipation.objects.filter(match=OuterRef("pk"), participant_number=2)
                .annotate(lower_name=Lower("bot__name"))
                .values("lower_name")[:1]
            )
            queryset = queryset.annotate(participant2_name=Subquery(subquery, output_field=CharField()))
            order_fields = [f.replace("participant2__bot__name", "participant2_name") for f in order_fields]

        return queryset.order_by(*order_fields)

    @property
    def qs(self):
        qs = super().qs

        qs = qs.select_related(
            "result",
            "map",
            "round",
            "round__competition",
        ).prefetch_related(
            Prefetch(
                "matchparticipation_set",
                queryset=MatchParticipation.objects.select_related("bot"),
            )
        )

        return qs


class MatchType(DjangoObjectTypeWithUID):
    participant1 = graphene.Field("aiarena.graphql.BotType")
    participant2 = graphene.Field("aiarena.graphql.BotType")
    status = graphene.String()
    result = graphene.Field("aiarena.graphql.ResultType")
    tags = DjangoConnectionField("aiarena.graphql.MatchTagType")

    class Meta:
        model = models.Match
        fields = ["status", "result", "map", "created", "started", "requested_by", "assigned_to", "round"]
        filterset_class = MatchFilterSet
        connection_class = CountingConnection

    @staticmethod
    def resolve_participant1(root: models.Match, info, **args):
        return root.participant1.bot

    @staticmethod
    def resolve_participant2(root: models.Match, info, **args):
        return root.participant2.bot

    @staticmethod
    def resolve_status(root: models.Match, info, **args):
        return root.status

    @staticmethod
    def resolve_result(root: models.Match, info, **args):
        return root.result


class MatchTagType(DjangoObjectTypeWithUID):
    tag = graphene.String()

    class Meta:
        model = models.MatchTag
        fields = ["id", "user"]
        filter_fields = []
        connection_class = CountingConnection

    @staticmethod
    def resolve_tag(root: models.MatchTag, info, **args):
        return root.tag.name


class MapFilterSet(FilterSet):
    name = django_filters.CharFilter(lookup_expr="icontains")

    class Meta:
        model = models.Map
        fields = ["name"]


class MapType(DjangoObjectTypeWithUID):
    download_link = graphene.String()

    class Meta:
        model = models.Map
        fields = ["name", "game_mode", "enabled"]
        filterset_class = MapFilterSet
        connection_class = CountingConnection

    @staticmethod
    def resolve_download_link(root: models.Map, info, **args):
        return info.context.build_absolute_uri(root.file.url)


class MapPoolFilterSet(FilterSet):
    order_by = OrderingFilter(fields=["enabled"])
    name = django_filters.CharFilter(lookup_expr="icontains")

    class Meta:
        model = models.MapPool
        fields = ["name", "order_by"]


class MapPoolType(DjangoObjectTypeWithUID):
    class Meta:
        model = models.MapPool
        fields = ["name", "maps", "enabled"]
        filterset_class = MapPoolFilterSet
        connection_class = CountingConnection


class NewsType(DjangoObjectTypeWithUID):
    class Meta:
        model = models.News
        fields = [
            "created",
            "title",
            "text",
            "yt_link",
        ]
        filter_fields = []
        connection_class = CountingConnection


class ResultType(DjangoObjectTypeWithUID):
    started = graphene.DateTime()
    participant1 = graphene.Field("aiarena.graphql.MatchParticipationType")
    participant2 = graphene.Field("aiarena.graphql.MatchParticipationType")
    game_time_formatted = graphene.String()
    replay_file = graphene.String()
    arenaclient_log = graphene.String()

    class Meta:
        model = models.Result
        fields = [
            "winner",
            "type",
            "created",
            "game_steps",
            "submitted_by",
        ]
        filter_fields = []
        connection_class = CountingConnection

    @staticmethod
    def resolve_replay_file(root: models.Result, info, **args):
        file = getattr(root, "replay_file", None)

        if not file:
            return None

        try:
            return file.url
        except Exception:
            return None

    @staticmethod
    def resolve_arenaclient_log(root: models.Result, info, **args):
        file = getattr(root, "arenaclient_log", None)

        if not file:
            return None

        try:
            return file.url
        except Exception:
            return None

    @staticmethod
    def resolve_started(root: models.Result, info, **args):
        return root.started

    @staticmethod
    def resolve_participant1(root: models.Result, info, **args):
        return root.participant1

    @staticmethod
    def resolve_participant2(root: models.Result, info, **args):
        return root.participant2

    @staticmethod
    def resolve_duration_seconds(root: models.Result, info, **args):
        return root.game_time_formatted


class RoundsType(DjangoObjectTypeWithUID):
    matches = DjangoConnectionField(MatchType)

    class Meta:
        model = models.Round
        fields = [
            "number",
            "started",
            "finished",
            "complete",
            "competition",
        ]
        filter_fields = []
        connection_class = CountingConnection

    @staticmethod
    def resolve_matches(root: models.Round, info, **kwargs):
        return root.match_set.all()


class StatsType(graphene.ObjectType):
    match_count_1h = graphene.Int()
    match_count_24h = graphene.Int()
    arenaclients = graphene.Int()
    random_supporter = graphene.Field("aiarena.graphql.UserType")
    build_number = graphene.String()
    date_time = graphene.DateTime()
    matches_queued = graphene.Int()
    matches_started = graphene.Int()

    @staticmethod
    def resolve_match_count_1h(root, info, **args):
        return Result.objects.only("id").filter(created__gte=timezone.now() - timedelta(hours=1)).count()

    @staticmethod
    def resolve_match_count_24h(root, info, **args):
        return Result.objects.only("id").filter(created__gte=timezone.now() - timedelta(hours=24)).count()

    @staticmethod
    def resolve_arenaclients(root, info, **args):
        return User.objects.only("id").filter(type="ARENA_CLIENT", is_active=True).count()

    @staticmethod
    def resolve_random_supporter(root, info, **args):
        return User.random_supporter()

    @staticmethod
    def resolve_build_number(root, info, **args):
        return settings.BUILD_NUMBER

    @staticmethod
    def resolve_date_time(root, info, **args):
        return timezone.now()

    @staticmethod
    def resolve_matches_queued(root, info, **args):
        return Match.objects.filter(
            result__isnull=True,
            started__isnull=True,
        ).count()

    @staticmethod
    def resolve_matches_started(root, info, **args):
        return Match.objects.filter(
            result__isnull=True,
            started__isnull=False,
        ).count()


class TrophyType(DjangoObjectTypeWithUID):
    trophy_icon_name = graphene.String()
    trophy_icon_image = graphene.String()

    class Meta:
        model = models.Trophy
        fields = [
            "name",
            "bot",
        ]

    def resolve_trophy_icon_name(root: models.Trophy, info):
        return root.icon.name if root.icon else None

    def resolve_trophy_icon_image(root: models.Trophy, info):
        return root.icon.image.url if root.icon and root.icon.image else None


class UserFilterSet(FilterSet):
    order_by = OrderingFilter(
        fields=[
            "date_joined",
            "username",
            "type",
        ],
        method="filter_order_by",
    )

    username = django_filters.CharFilter(lookup_expr="icontains")
    only_with_bots = django_filters.BooleanFilter(method="filter_only_with_bots")

    class Meta:
        model = models.User
        fields = [
            "username",
            "order_by",
            "type",
            "only_with_bots",
        ]

    def filter_order_by(self, queryset, name, value):
        order_fields = value if isinstance(value, list) else [value]
        return queryset.order_by(*order_fields)

    def filter_only_with_bots(self, queryset, name, value):
        if value:
            return queryset.annotate(bot_count=Count("bots")).filter(bot_count__gt=0)
        return queryset


class UserType(DjangoObjectTypeWithUID):
    # This is the public user type.
    # put data everyone should be able view here.

    bots = DjangoFilterConnectionField("aiarena.graphql.BotType")
    avatar_url = graphene.String()

    class Meta:
        model = models.User
        fields = ["id", "username", "patreon_level", "date_joined", "type"]
        filterset_class = UserFilterSet

    @staticmethod
    def resolve_bots(root: models.User, info, **args):
        return root.bots.order_by("-bot_zip_updated")

    @staticmethod
    def resolve_avatar_url(root: models.User, info):
        avatar_instance = Avatar.objects.filter(user=root).order_by("-primary", "-date_uploaded").first()

        if avatar_instance:
            avatar_url = avatar_instance.get_absolute_url()
            return info.context.build_absolute_uri(avatar_url)
            # We can also return "avatar_url" if we want a relative url
            # return  avatar_url
        return None  # Return None if no avatar exists. However, we probably want to return the default avatar.


class Viewer(graphene.ObjectType):
    # This is the private viewer user type.
    # Put data only the logged in user should be able view here.
    user = graphene.Field("aiarena.graphql.UserType")
    id = graphene.ID(required=True)
    api_token = graphene.String()
    email = graphene.String()
    active_bot_participations = graphene.Int()
    active_bot_participation_limit = graphene.Int()
    request_matches_limit = graphene.Int(required=True)
    request_matches_count_left = graphene.Int(required=True)
    requested_matches = DjangoFilterConnectionField("aiarena.graphql.MatchType", filterset_class=MatchFilterSet)
    receive_email_comms = graphene.Boolean()
    last_login = graphene.DateTime()
    date_joined = graphene.DateTime()
    first_name = graphene.String()
    last_name = graphene.String()
    linked_discord = graphene.Boolean()
    linked_patreon = graphene.Boolean()

    @staticmethod
    def resolve_id(root: models.User, info, **args):
        # It represents the current logged-in user, and is unique
        return "viewer"

    @staticmethod
    def resolve_user(root: models.User, info, **args):
        return root

    @staticmethod
    def resolve_api_token(root: models.User, info):
        try:
            token = Token.objects.get(user=info.context.user)
        except Token.DoesNotExist:
            token = "no token - contact us"

        return token

    @staticmethod
    def resolve_email(root: models.User, info):
        return root.email

    @staticmethod
    def resolve_active_bot_participations(root: models.User, info, **args):
        return users.get_total_active_competition_participations(root)

    @staticmethod
    def resolve_active_bot_participation_limit(root: models.User, info, **args):
        return supporters.get_active_bots_limit(root)

    @staticmethod
    def resolve_request_matches_limit(root: models.User, info, **args):
        return supporters.get_requested_matches_limit(root)

    @staticmethod
    def resolve_request_matches_count_left(root: models.User, info, **args):
        return match_requests.get_user_match_request_count_left(root)

    @staticmethod
    def resolve_requested_matches(root: models.User, info, **args):
        return root.requested_matches.order_by("-started", "-id")

    @staticmethod
    def resolve_receive_email_comms(root: models.User, info):
        return root.receive_email_comms

    @staticmethod
    def resolve_last_login(root: models.User, info):
        return root.last_login

    @staticmethod
    def resolve_date_joined(root: models.User, info):
        return root.date_joined

    @staticmethod
    def resolve_first_name(root: models.User, info):
        return root.first_name

    @staticmethod
    def resolve_last_name(root: models.User, info):
        return root.last_name

    @staticmethod
    def resolve_linked_discord(root: models.User, info):
        return getattr(root, "discord_user", None) is not None

    @staticmethod
    def resolve_linked_patreon(root: models.User, info):
        return getattr(root, "patreonaccountbind", None) is not None


class Query(graphene.ObjectType):
    bot_race = DjangoFilterConnectionField("aiarena.graphql.BotRaceType")
    bots = DjangoFilterConnectionField("aiarena.graphql.BotType")
    competitions = DjangoFilterConnectionField("aiarena.graphql.CompetitionType")
    map_pools = DjangoFilterConnectionField("aiarena.graphql.MapPoolType")
    maps = DjangoFilterConnectionField("aiarena.graphql.MapType")
    match = DjangoFilterConnectionField("aiarena.graphql.MatchType")
    news = DjangoFilterConnectionField("aiarena.graphql.NewsType")
    node = graphene.relay.Node.Field()
    results = DjangoFilterConnectionField("aiarena.graphql.ResultType")
    rounds = DjangoFilterConnectionField("aiarena.graphql.RoundsType")
    stats = graphene.Field(StatsType)
    users = DjangoFilterConnectionField("aiarena.graphql.UserType")
    viewer = graphene.Field("aiarena.graphql.Viewer")
    match_participations = DjangoFilterConnectionField("aiarena.graphql.MatchParticipationType")

    @staticmethod
    def resolve_bot_race(root, info, **args):
        return models.BotRace.objects.all()

    @staticmethod
    def resolve_bots(root, info, **args):
        return models.Bot.objects.all()

    @staticmethod
    def resolve_competitions(root, info, **args):
        return models.Competition.objects.all()

    @staticmethod
    def resolve_map_pools(root, info, **args):
        return models.MapPool.objects.all().order_by("-id")

    @staticmethod
    def resolve_maps(root, info, **args):
        return models.Map.objects.all()

    @staticmethod
    def resolve_match(root, info, **args):
        return models.Match.objects.all()

    @staticmethod
    def resolve_news(root, info, **args):
        return models.News.objects.all().order_by("-created")

    @staticmethod
    def resolve_results(root, info, **args):
        return models.Result.objects.all().order_by("-created")

    @staticmethod
    def resolve_rounds(root, info, **args):
        return models.Round.objects.all().order_by("-started")

    @staticmethod
    def resolve_stats(root, info, **args):
        return StatsType()

    @staticmethod
    def resolve_users(root, info, **args):
        return models.User.objects.all()

    @staticmethod
    def resolve_viewer(root, info, **args):
        if info.context.user.is_authenticated:
            return info.context.user
        return None
