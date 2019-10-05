import logging

from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import viewsets, serializers
from rest_framework.filters import SearchFilter, OrderingFilter

from aiarena.core.models import Match, Result, Bot, Map, User, Round, Participant

logger = logging.getLogger(__name__)

# !IMPORTANT!
# Serializer and Filter/etc fields are manually specified for security reasons
# Allowing filtering/etc on sensitive fields could leak information.
# Serializer fields are also manually specified so new private fields don't accidentally get leaked.

bot_include_fields = 'id', 'user', 'name', 'created', 'active', 'in_match', \
                     'current_match', 'elo', 'plays_race', 'type', 'game_display_id', 'bot_zip_updated',
map_include_fields = 'id', 'name', 'active',
match_include_fields = 'id', 'map', 'created', 'started', 'assigned_to', 'round',
participant_include_fields = 'id', 'match', 'participant_number', 'bot', 'resultant_elo', 'elo_change', 'avg_step_time',
# todo: add 'arenaclient_log',
result_include_fields = 'id', 'match', 'winner', 'type', 'created', 'replay_file', \
                        'game_steps', 'submitted_by', 'arenaclient_log',
result_filter_fields = 'id', 'match', 'winner', 'type', 'created', 'game_steps', 'submitted_by',
round_include_fields = 'id', 'started', 'finished', 'complete',
user_include_fields = 'id', 'username', 'first_name', 'last_name', 'is_staff', 'is_active', 'date_joined', \
                      'service_account', 'patreon_level'


class BotSerializer(serializers.ModelSerializer):
    class Meta:
        model = Bot
        fields = bot_include_fields


class BotViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Bot data view
    """
    queryset = Bot.objects.all()
    serializer_class = BotSerializer

    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = bot_include_fields
    search_fields = bot_include_fields
    ordering_fields = bot_include_fields


class MapSerializer(serializers.ModelSerializer):
    class Meta:
        model = Map
        # todo: The file isn't used by the arena clients currently, so exclude it to avoid confusion.
        # todo: Eventually the arena clients will download maps from the website
        fields = map_include_fields


class MapViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Map data view
    """
    queryset = Map.objects.all()
    serializer_class = MapSerializer

    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = map_include_fields
    search_fields = map_include_fields
    ordering_fields = map_include_fields


class MatchSerializer(serializers.ModelSerializer):
    class Meta:
        model = Match
        fields = match_include_fields


class MatchViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Match data view
    """
    queryset = Match.objects.all()
    serializer_class = MatchSerializer

    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = match_include_fields
    search_fields = match_include_fields
    ordering_fields = match_include_fields


class ParticipantSerializer(serializers.ModelSerializer):
    class Meta:
        model = Participant
        fields = participant_include_fields


class ParticipantViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Result data view
    """
    queryset = Participant.objects.all()
    serializer_class = ParticipantSerializer

    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = participant_include_fields
    search_fields = participant_include_fields
    ordering_fields = participant_include_fields

# todo: bot names are included for the stream to use. Ideally the the stream should properly utilize the API
class ResultSerializer(serializers.ModelSerializer):
    bot1_name = serializers.SerializerMethodField()
    bot2_name = serializers.SerializerMethodField()

    def get_bot1_name(self, obj):
        return obj.match.participant_set.get(participant_number=1).bot.name

    def get_bot2_name(self, obj):
        return obj.match.participant_set.get(participant_number=2).bot.name

    class Meta:
        model = Result
        fields = result_include_fields + ('bot1_name', 'bot2_name')


class ResultViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Result data view
    """
    queryset = Result.objects.all()
    serializer_class = ResultSerializer

    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = result_filter_fields
    search_fields = result_filter_fields
    ordering_fields = result_filter_fields


class RoundSerializer(serializers.ModelSerializer):
    class Meta:
        model = Round
        fields = round_include_fields


class RoundViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Result data view
    """
    queryset = Round.objects.all()
    serializer_class = RoundSerializer

    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = round_include_fields
    search_fields = round_include_fields
    ordering_fields = round_include_fields


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = user_include_fields


class UserViewSet(viewsets.ReadOnlyModelViewSet):
    """
    User data view
    """
    queryset = User.objects.all()
    serializer_class = UserSerializer

    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = user_include_fields
    search_fields = user_include_fields
    ordering_fields = user_include_fields
