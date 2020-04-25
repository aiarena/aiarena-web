import logging
from wsgiref.util import FileWrapper

from django.http import HttpResponse, Http404
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import viewsets, serializers
from rest_framework.decorators import action
from rest_framework.filters import SearchFilter, OrderingFilter
from rest_framework.reverse import reverse
from django.db.models import Prefetch

from aiarena.core.models import Match, Result, Bot, Map, User, Round, MatchParticipation, SeasonParticipation, Season

logger = logging.getLogger(__name__)

# !ATTENTION! IF YOU CHANGE THE API ANNOUNCE IT TO USERS

# !IMPORTANT!
# Serializer and Filter/etc fields are manually specified for security reasons
# Allowing filtering/etc on sensitive fields could leak information.
# Serializer fields are also manually specified so new private fields don't accidentally get leaked.

bot_include_fields = 'id', 'user', 'name', 'created', 'active', 'plays_race', 'type', \
                     'game_display_id', 'bot_zip_updated', 'bot_zip_publicly_downloadable', 'bot_zip', \
                     'bot_zip_md5hash', 'bot_data_publicly_downloadable', 'bot_data', 'bot_data_md5hash'
bot_filter_fields = {
    'id': ['exact', 'lt', 'gt', 'lte', 'gte'],
    'user': ['exact'],
    'name': ['exact'],
    'created': ['exact', 'lt', 'gt', 'lte', 'gte'],
    'active': ['exact'],
    'plays_race': ['exact'],
    'type': ['exact'],
    'game_display_id': ['exact'],
    'bot_zip_updated': ['exact', 'lt', 'gt', 'lte', 'gte'],
    'bot_zip_publicly_downloadable': ['exact'],
    'bot_data_publicly_downloadable': ['exact']
}
bot_search_fields = 'id', 'user', 'name', 'created', 'active', 'plays_race', 'type', \
                    'game_display_id', 'bot_zip_updated', 'bot_zip_publicly_downloadable', 'bot_data_publicly_downloadable'
map_include_fields = 'id', 'name', 'file', 'active',
map_filter_fields = 'id', 'name', 'active',
match_include_fields = 'id', 'map', 'created', 'started', 'assigned_to', 'round', 'requested_by',
matchparticipation_include_fields = 'id', 'match', 'participant_number', 'bot', 'starting_elo', 'resultant_elo', \
                                    'elo_change', 'avg_step_time', 'match_log', 'result', 'result_cause',
matchparticipation_filter_fields = 'id', 'match', 'participant_number', 'bot', 'starting_elo', 'resultant_elo', \
                                   'elo_change', 'avg_step_time', 'result', 'result_cause',
result_include_fields = 'id', 'match', 'winner', 'type', 'created', 'replay_file', 'game_steps', \
                        'submitted_by', 'arenaclient_log', 'interest_rating', 'date_interest_rating_calculated',
result_filter_fields = {
    'id': ['exact', 'lt', 'gt', 'lte', 'gte'],
    'match': ['exact', 'lt', 'gt', 'lte', 'gte'],
    'winner': ['exact'],
    'type': ['exact'],
    'created': ['exact', 'lt', 'gt', 'lte', 'gte'],
    'game_steps': ['exact', 'lt', 'gt', 'lte', 'gte'],
    'submitted_by': ['exact'],
    'interest_rating': ['exact', 'lt', 'gt', 'lte', 'gte'],
    'date_interest_rating_calculated': ['exact', 'lt', 'gt', 'lte', 'gte']
}
result_search_fields = 'id', 'match', 'winner', 'type', 'created', 'game_steps', \
                       'submitted_by', 'interest_rating', 'date_interest_rating_calculated',
round_include_fields = 'id', 'number', 'season', 'started', 'finished', 'complete',
season_include_fields = 'id', 'number', 'date_created', 'date_opened', 'date_closed', 'status',
seasonparticipation_include_fields = 'id', 'season', 'bot', 'elo',
user_include_fields = 'id', 'username', 'first_name', 'last_name', 'is_staff', 'is_active', 'date_joined', \
                      'type', 'patreon_level'


# !ATTENTION! IF YOU CHANGE THE API ANNOUNCE IT TO USERS


class BotSerializer(serializers.ModelSerializer):
    bot_zip = serializers.SerializerMethodField()
    bot_zip_md5hash = serializers.SerializerMethodField()
    bot_data = serializers.SerializerMethodField()
    bot_data_md5hash = serializers.SerializerMethodField()

    def get_bot_zip(self, obj):
        # only display if the user can download the file
        if obj.bot_zip and obj.can_download_bot_zip(self.context['request'].user):
            # provide an API based download url instead of website.
            return reverse('api_bot-download-zip', kwargs={'pk': obj.id}, request=self.context['request'])
        else:
            return None

    def get_bot_zip_md5hash(self, obj):
        # only display if the user can download the file
        if obj.can_download_bot_zip(self.context['request'].user):
            return obj.bot_zip_md5hash
        else:
            return None

    def get_bot_data(self, obj):
        # only display if the user can download the file
        if obj.bot_data and obj.can_download_bot_data(self.context['request'].user):
            # provide an API based download url instead of website.
            return reverse('api_bot-download-data', kwargs={'pk': obj.id}, request=self.context['request'])
        else:
            return None

    def get_bot_data_md5hash(self, obj):
        # only display if the user can download the file
        if obj.can_download_bot_data(self.context['request'].user):
            return obj.bot_data_md5hash
        else:
            return None

    class Meta:
        model = Bot
        fields = bot_include_fields


# !ATTENTION! IF YOU CHANGE THE API ANNOUNCE IT TO USERS

class BotViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Bot data view
    """
    queryset = Bot.objects.all()
    serializer_class = BotSerializer

    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = bot_filter_fields
    search_fields = bot_search_fields
    ordering_fields = bot_search_fields

    @action(detail=True, methods=['GET'], name='Download a bot\'s zip file', url_path='zip')
    def download_zip(self, request, *args, **kwargs):
        bot = Bot.objects.get(id=kwargs['pk'])
        if bot.can_download_bot_zip(request.user):
            response = HttpResponse(FileWrapper(bot.bot_zip), content_type='application/zip')
            response['Content-Disposition'] = 'inline; filename="{0}.zip"'.format(bot.name)
            return response
        else:
            raise Http404()

    @action(detail=True, methods=['GET'], name='Download a bot\'s data file', url_path='data')
    def download_data(self, request, *args, **kwargs):
        bot = Bot.objects.get(id=kwargs['pk'])
        if bot.can_download_bot_data(request.user):
            response = HttpResponse(FileWrapper(bot.bot_data), content_type='application/zip')
            response['Content-Disposition'] = 'inline; filename="{0}_data.zip"'.format(bot.name)
            return response
        else:
            raise Http404()


# !ATTENTION! IF YOU CHANGE THE API ANNOUNCE IT TO USERS

class MapSerializer(serializers.ModelSerializer):
    class Meta:
        model = Map
        fields = map_include_fields


# !ATTENTION! IF YOU CHANGE THE API ANNOUNCE IT TO USERS

class MapViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Map data view
    """
    queryset = Map.objects.all()
    serializer_class = MapSerializer

    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = map_filter_fields
    search_fields = map_filter_fields
    ordering_fields = map_filter_fields


# !ATTENTION! IF YOU CHANGE THE API ANNOUNCE IT TO USERS

class MatchParticipationSerializer(serializers.ModelSerializer):
    match_log = serializers.SerializerMethodField()

    def get_match_log(self, obj):
        # only display if the user can download the file
        if obj.match_log and obj.can_download_match_log(self.context['request'].user):
            # provide an API based download url instead of website.
            return reverse('api_matchparticipation-download-match-log', kwargs={'pk': obj.id},
                           request=self.context['request'])
        else:
            return None

    class Meta:
        model = MatchParticipation
        fields = matchparticipation_include_fields


# !ATTENTION! IF YOU CHANGE THE API ANNOUNCE IT TO USERS

class MatchParticipationViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Result data view
    """
    queryset = MatchParticipation.objects.all()
    serializer_class = MatchParticipationSerializer

    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = matchparticipation_filter_fields
    search_fields = matchparticipation_filter_fields
    ordering_fields = matchparticipation_filter_fields

    @action(detail=True, methods=['GET'], name='Download a bot\'s zip file', url_path='match-log')
    def download_match_log(self, request, *args, **kwargs):
        mp = MatchParticipation.objects.get(id=kwargs['pk'])
        if mp.can_download_match_log(request.user):
            response = HttpResponse(FileWrapper(mp.match_log), content_type='application/zip')
            response['Content-Disposition'] = f'inline; filename="{mp.match_id}_{mp.bot.name}.zip"'
            return response
        else:
            raise Http404()


# !ATTENTION! IF YOU CHANGE THE API ANNOUNCE IT TO USERS

class SeasonParticipationSerializer(serializers.ModelSerializer):
    class Meta:
        model = SeasonParticipation
        fields = seasonparticipation_include_fields


# !ATTENTION! IF YOU CHANGE THE API ANNOUNCE IT TO USERS

class SeasonParticipationViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Result data view
    """
    queryset = SeasonParticipation.objects.all()
    serializer_class = SeasonParticipationSerializer

    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = seasonparticipation_include_fields
    search_fields = seasonparticipation_include_fields
    ordering_fields = seasonparticipation_include_fields


# !ATTENTION! IF YOU CHANGE THE API ANNOUNCE IT TO USERS

# todo: bot names are included for the stream to use. Ideally the the stream should properly utilize the API
class ResultSerializer(serializers.ModelSerializer):
    bot1_name = serializers.SerializerMethodField()
    bot2_name = serializers.SerializerMethodField()

    def get_bot1_name(self, obj):
        return obj.match.participant1.bot.name

    def get_bot2_name(self, obj):
        return obj.match.participant2.bot.name

    class Meta:
        model = Result
        fields = result_include_fields + ('bot1_name', 'bot2_name')


# !ATTENTION! IF YOU CHANGE THE API ANNOUNCE IT TO USERS

class ResultViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Result data view
    """
    queryset = Result.objects.all().prefetch_related(
        Prefetch('winner'),
        Prefetch('match__matchparticipation_set', MatchParticipation.objects.all().prefetch_related('bot'),
                 to_attr='participants'))
    serializer_class = ResultSerializer

    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = result_filter_fields
    search_fields = result_search_fields
    ordering_fields = result_search_fields


# !ATTENTION! IF YOU CHANGE THE API ANNOUNCE IT TO USERS

class MatchSerializer(serializers.ModelSerializer):
    result = ResultSerializer()
    class Meta:
        model = Match
        fields = match_include_fields + ('result',)


# !ATTENTION! IF YOU CHANGE THE API ANNOUNCE IT TO USERS

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


# !ATTENTION! IF YOU CHANGE THE API ANNOUNCE IT TO USERS

class RoundSerializer(serializers.ModelSerializer):
    class Meta:
        model = Round
        fields = round_include_fields


# !ATTENTION! IF YOU CHANGE THE API ANNOUNCE IT TO USERS

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


# !ATTENTION! IF YOU CHANGE THE API ANNOUNCE IT TO USERS

class SeasonSerializer(serializers.ModelSerializer):
    class Meta:
        model = Season
        fields = season_include_fields


# !ATTENTION! IF YOU CHANGE THE API ANNOUNCE IT TO USERS

class SeasonViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Result data view
    """
    queryset = Season.objects.all()
    serializer_class = SeasonSerializer

    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = season_include_fields
    search_fields = season_include_fields
    ordering_fields = season_include_fields


# !ATTENTION! IF YOU CHANGE THE API ANNOUNCE IT TO USERS

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = user_include_fields


# !ATTENTION! IF YOU CHANGE THE API ANNOUNCE IT TO USERS

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

# !ATTENTION! IF YOU CHANGE THE API ANNOUNCE IT TO USERS
