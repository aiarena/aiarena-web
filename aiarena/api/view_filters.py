from django_filters import rest_framework as filters
from django.db.models import Q
from rest_framework.exceptions import ValidationError

from aiarena.core.models import Match, Result, Bot, Map, User, Round, MatchParticipation, CompetitionParticipation, Competition


# Filter for items containing ALL tags in comma separated string
# If passed value contains a "|", then it will filter for items containing tags by ANY users in comma separated string on LHS of separator
class TagsFilter(filters.CharFilter):
    def __init__(self, field_name2, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.field_name2 = field_name2

    def filter(self, qs, value):
        if not value:
            return qs

        # Check for pipe separator
        if '|' in value:
            users_str, tags_str = [s.strip() for s in value.split('|')]
        else:
            users_str = ""
            tags_str = value

        # Build query for users
        user_query = Q()
        if users_str:
            try:
                users = [int(s) for s in users_str.split(',')]
            except ValueError:
                raise ValidationError("When using pipe separator (\"|\"), Expecting user_id (int) on LHS and tag_name on RHS of separator.")
            lookup = '%s__%s' % (self.field_name2, self.lookup_expr)
            for v in users:
                user_query = user_query | Q(**{lookup: v})

        # Build query for tags
        tag_query = Q()
        if tags_str:
            tags = [s.strip() for s in tags_str.split(',')]
            lookup = '%s__%s' % (self.field_name, self.lookup_expr)
            for v in tags:
                if v:
                    tag_query = tag_query & Q(**{lookup: v})
        
        return self.get_method(qs)(user_query & tag_query)


# Filter for the API views
# Should create manual filters for referenced fields, otherwise there will be duplicate queries
class BotFilter(filters.FilterSet):
    min_created = filters.NumberFilter(field_name="created", lookup_expr='gte')
    max_created = filters.NumberFilter(field_name="created", lookup_expr='lte')
    min_user = filters.NumberFilter(field_name="user", lookup_expr='gte')
    max_user = filters.NumberFilter(field_name="user", lookup_expr='lte')
    user = filters.NumberFilter(field_name="user")

    class Meta:
        model = Bot
        fields = [
            'id',
            'name',
            'created',
            'plays_race',
            'type',
            'game_display_id',
            'bot_zip_updated',
            'bot_zip_publicly_downloadable',
            'bot_data_publicly_downloadable'
        ]


class MatchParticipationFilter(filters.FilterSet):
    min_match = filters.NumberFilter(field_name="match_id", lookup_expr='gte')
    max_match = filters.NumberFilter(field_name="match_id", lookup_expr='lte')
    match = filters.NumberFilter(field_name="match_id")
    bot = filters.NumberFilter(field_name="bot_id")
    min_avg_step_time = filters.NumberFilter(field_name="avg_step_time", lookup_expr='gte')
    max_avg_step_time = filters.NumberFilter(field_name="avg_step_time", lookup_expr='lte')
    avg_step_time = filters.NumberFilter(field_name="avg_step_time")
    tags = TagsFilter(field_name="match__tags__tag__name", field_name2="match__tags__user")

    class Meta:
        model = MatchParticipation
        fields = [
            'id',
            'participant_number',
            'starting_elo',
            'resultant_elo',
            'elo_change',
            'avg_step_time',
            'result',
            'result_cause'
        ]


class ResultFilter(filters.FilterSet):
    min_match = filters.NumberFilter(field_name="match_id", lookup_expr='gte')
    max_match = filters.NumberFilter(field_name="match_id", lookup_expr='lte')
    match = filters.NumberFilter(field_name="match_id")
    min_created = filters.NumberFilter(field_name="created", lookup_expr='gte')
    max_created = filters.NumberFilter(field_name="created", lookup_expr='lte')
    min_game_steps = filters.NumberFilter(field_name="avg_step_time", lookup_expr='gte')
    max_game_steps = filters.NumberFilter(field_name="avg_step_time", lookup_expr='lte')
    winner = filters.NumberFilter(field_name="winner")
    submitted_by = filters.NumberFilter(field_name="submitted_by")

    class Meta:
        model = Result
        fields = [
            'id',
            'type',
            'created',
            'game_steps',
            'interest_rating',
            'date_interest_rating_calculated'
        ]


class MatchFilter(filters.FilterSet):
    min_round = filters.NumberFilter(field_name="round_id", lookup_expr='gte')
    max_round = filters.NumberFilter(field_name="round_id", lookup_expr='lte')
    round = filters.NumberFilter(field_name="round_id")
    min_created = filters.NumberFilter(field_name="created", lookup_expr='gte')
    max_created = filters.NumberFilter(field_name="created", lookup_expr='lte')
    assigned_to = filters.NumberFilter(field_name="assigned_to")
    requested_by = filters.NumberFilter(field_name="requested_by")
    map = filters.NumberFilter(field_name="map")
    tags = TagsFilter(field_name="tags__tag__name", field_name2="tags__user")
    
    class Meta:
        model = Match
        fields = [
            'id',
            'created',
            'started'
        ]
