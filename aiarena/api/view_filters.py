from django_filters import rest_framework as filters

from aiarena.core.d_utils import filter_tags
from aiarena.core.models import (
    Bot,
    Competition,
    CompetitionParticipation,
    Map,
    Match,
    MatchParticipation,
    Result,
    Round,
    User,
)


# Filter for the API views
# Should create manual filters for referenced fields, otherwise there will be duplicate queries
class BotFilter(filters.FilterSet):
    min_created = filters.NumberFilter(field_name="created", lookup_expr="gte")
    max_created = filters.NumberFilter(field_name="created", lookup_expr="lte")
    min_user = filters.NumberFilter(field_name="user", lookup_expr="gte")
    max_user = filters.NumberFilter(field_name="user", lookup_expr="lte")
    user = filters.NumberFilter(field_name="user")

    class Meta:
        model = Bot
        fields = [
            "id",
            "name",
            "created",
            "plays_race",
            "type",
            "game_display_id",
            "bot_zip_updated",
            "bot_zip_publicly_downloadable",
            "bot_data_publicly_downloadable",
        ]


class MatchParticipationFilter(filters.FilterSet):
    min_match = filters.NumberFilter(field_name="match_id", lookup_expr="gte")
    max_match = filters.NumberFilter(field_name="match_id", lookup_expr="lte")
    match = filters.NumberFilter(field_name="match_id")
    bot = filters.NumberFilter(field_name="bot_id")
    min_avg_step_time = filters.NumberFilter(field_name="avg_step_time", lookup_expr="gte")
    max_avg_step_time = filters.NumberFilter(field_name="avg_step_time", lookup_expr="lte")
    avg_step_time = filters.NumberFilter(field_name="avg_step_time")

    class Meta:
        model = MatchParticipation
        fields = [
            "id",
            "participant_number",
            "starting_elo",
            "resultant_elo",
            "elo_change",
            "avg_step_time",
            "result",
            "result_cause",
        ]


class ResultFilter(filters.FilterSet):
    min_match = filters.NumberFilter(field_name="match_id", lookup_expr="gte")
    max_match = filters.NumberFilter(field_name="match_id", lookup_expr="lte")
    match = filters.NumberFilter(field_name="match_id")
    min_created = filters.NumberFilter(field_name="created", lookup_expr="gte")
    max_created = filters.NumberFilter(field_name="created", lookup_expr="lte")
    min_game_steps = filters.NumberFilter(field_name="avg_step_time", lookup_expr="gte")
    max_game_steps = filters.NumberFilter(field_name="avg_step_time", lookup_expr="lte")
    winner = filters.NumberFilter(field_name="winner")
    submitted_by = filters.NumberFilter(field_name="submitted_by")

    class Meta:
        model = Result
        fields = ["id", "type", "created", "game_steps", "interest_rating", "date_interest_rating_calculated"]


class MatchFilter(filters.FilterSet):
    min_round = filters.NumberFilter(field_name="round_id", lookup_expr="gte")
    max_round = filters.NumberFilter(field_name="round_id", lookup_expr="lte")
    round = filters.NumberFilter(field_name="round_id")
    min_created = filters.NumberFilter(field_name="created", lookup_expr="gte")
    max_created = filters.NumberFilter(field_name="created", lookup_expr="lte")
    assigned_to = filters.NumberFilter(field_name="assigned_to")
    requested_by = filters.NumberFilter(field_name="requested_by")
    map = filters.NumberFilter(field_name="map")
    bot = filters.NumberFilter(field_name="matchparticipation__bot")
    tags = filters.CharFilter(method="filter_tags__exact")
    tags__icontains = filters.CharFilter(method="filter_tags__icontains")

    class Meta:
        model = Match
        fields = ["id", "created", "started"]

    def filter_tags__exact(self, qs, name, value):
        return filter_tags(qs, value, "tags__tag__name", "iexact", "tags__user")

    def filter_tags__icontains(self, qs, name, value):
        return filter_tags(qs, value, "tags__tag__name", "icontains", "tags__user")
