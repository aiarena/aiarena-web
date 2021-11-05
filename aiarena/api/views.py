import logging
from wsgiref.util import FileWrapper

from discord_bind.models import DiscordUser
from django.db.models import Prefetch
from django.http import HttpResponse, Http404
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import viewsets, serializers
from rest_framework.decorators import action
from rest_framework.filters import SearchFilter, OrderingFilter
from rest_framework.reverse import reverse

from aiarena.api.view_filters import BotFilter, MatchParticipationFilter, ResultFilter, MatchFilter
from aiarena.core.models import Match, Result, Bot, Map, User, Round, MatchParticipation, CompetitionParticipation, \
    Competition, MatchTag, Game, GameMode, MapPool, CompetitionBotMatchupStats, News, Trophy
from aiarena.core.permissions import IsServiceOrAdminUser

logger = logging.getLogger(__name__)

# !ATTENTION! IF YOU CHANGE THE API ANNOUNCE IT TO USERS

# !IMPORTANT!
# Serializer and Filter/etc fields are manually specified for security reasons
# Allowing filtering/etc on sensitive fields could leak information.
# Serializer fields are also manually specified so new private fields don't accidentally get leaked.

bot_include_fields = 'id', 'user', 'name', 'created', 'bot_zip', 'bot_zip_updated', 'bot_zip_md5hash', \
                     'bot_zip_publicly_downloadable', 'bot_data_enabled', 'bot_data', 'bot_data_md5hash', \
                     'bot_data_publicly_downloadable', 'plays_race', 'type', 'game_display_id',
bot_search_fields = 'id', 'user', 'name', 'created', 'bot_zip_updated', 'bot_zip_publicly_downloadable', \
                    'bot_data_enabled', 'bot_data_publicly_downloadable', 'plays_race', 'type', 'game_display_id',
competition_include_fields = 'id', 'name', 'type', 'game_mode', 'date_created', 'date_opened', 'date_closed', \
                             'status', 'max_active_rounds', 'interest', 'target_n_divisions', 'n_divisions', \
                             'target_division_size', 'rounds_per_cycle', 'rounds_this_cycle', 'n_placements',
competition_bot_matchup_stats_include_fields = 'bot', 'opponent', 'match_count', 'win_count', 'win_perc', 'loss_count', \
                                               'loss_perc', 'tie_count', 'tie_perc', 'crash_count', 'crash_perc', \
                                               'updated',
competition_participation_include_fields = 'id', 'competition', 'bot', 'elo', 'match_count', 'win_perc', 'win_count', \
                                           'loss_perc', 'loss_count', 'tie_perc', 'tie_count', 'crash_perc', \
                                           'crash_count', 'elo_graph', 'highest_elo', 'slug', 'active', \
                                           'division_num', 'in_placements',
competition_participation_filter_fields = 'id', 'competition', 'bot', 'elo', 'match_count', 'win_perc', 'win_count', \
                                          'loss_perc', 'loss_count', 'tie_perc', 'tie_count', 'crash_perc', \
                                          'crash_count', 'highest_elo', 'slug', 'active', \
                                          'division_num', 'in_placements',
discord_user_include_fields = 'user', 'uid',
game_include_fields = 'id', 'name',
game_mode_include_fields = 'id', 'name', 'game',
map_include_fields = 'id', 'name', 'file', 'game_mode', 'competitions', 'enabled',
map_filter_fields = 'id', 'name', 'game_mode', 'competitions', 'enabled',
map_pool_include_fields = 'id', 'name', 'maps', 'enabled',
match_include_fields = 'id', 'map', 'created', 'started', 'assigned_to', 'round', 'requested_by', \
                       'require_trusted_arenaclient'
matchparticipation_include_fields = 'id', 'match', 'participant_number', 'bot', 'starting_elo', 'resultant_elo', \
                                    'elo_change', 'match_log', 'avg_step_time', 'result', 'result_cause', \
                                    'use_bot_data', 'update_bot_data', 'match_log_has_been_cleaned',
matchparticipation_filter_fields = 'id', 'match', 'participant_number', 'bot', 'starting_elo', 'resultant_elo', \
                                   'elo_change', 'avg_step_time', 'result', 'result_cause', 'use_bot_data', \
                                   'update_bot_data', 'match_log_has_been_cleaned',
matchtag_include_fields = 'user', 'tag_name'
news_include_fields = 'id', 'created', 'title', 'text', 'yt_link',
result_include_fields = 'id', 'match', 'winner', 'type', 'created', 'replay_file', 'game_steps', \
                        'submitted_by', 'arenaclient_log', 'interest_rating', 'date_interest_rating_calculated', \
                        'replay_file_has_been_cleaned', 'arenaclient_log_has_been_cleaned',
result_search_fields = 'id', 'match', 'winner', 'type', 'created', 'game_steps', \
                       'submitted_by', 'interest_rating', 'date_interest_rating_calculated', \
                       'replay_file_has_been_cleaned', 'arenaclient_log_has_been_cleaned',
round_include_fields = 'id', 'number', 'competition', 'started', 'finished', 'complete',
trophy_include_fields = 'id', 'icon', 'bot', 'name',
trophy_icon_include_fields = 'id', 'name', 'image',
trophy_icon_filter_fields = 'id', 'name',
user_include_fields = 'id', 'username', 'first_name', 'last_name', 'is_staff', 'is_active', 'date_joined', \
                      'patreon_level', 'type',


# !ATTENTION! IF YOU CHANGE THE API ANNOUNCE IT TO USERS
# This is out of order, because it's used by the BotSerializer
class TrophySerializer(serializers.ModelSerializer):
    trophy_icon_name = serializers.SerializerMethodField()

    def get_trophy_icon_name(self, obj):
        return obj.icon.name

    trophy_icon_image = serializers.SerializerMethodField()

    def get_trophy_icon_image(self, obj):
        return obj.icon.image

    class Meta:
        model = Trophy
        fields = trophy_include_fields


class BotSerializer(serializers.ModelSerializer):
    bot_zip = serializers.SerializerMethodField()
    bot_zip_md5hash = serializers.SerializerMethodField()
    bot_data = serializers.SerializerMethodField()
    bot_data_md5hash = serializers.SerializerMethodField()
    trophies = TrophySerializer(many=True)

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
        fields = bot_include_fields + ('trophies',)
        ref_name = "website"


# !ATTENTION! IF YOU CHANGE THE API ANNOUNCE IT TO USERS

class BotViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Bot data view
    """
    queryset = Bot.objects.all().select_related('user')
    serializer_class = BotSerializer

    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_class = BotFilter
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

class CompetitionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Competition
        fields = competition_include_fields


# !ATTENTION! IF YOU CHANGE THE API ANNOUNCE IT TO USERS

class CompetitionViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Competition data view
    """
    queryset = Competition.objects.all()
    serializer_class = CompetitionSerializer

    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = competition_include_fields
    search_fields = competition_include_fields
    ordering_fields = competition_include_fields


# !ATTENTION! IF YOU CHANGE THE API ANNOUNCE IT TO USERS

class CompetitionBotMatchupStatsSerializer(serializers.ModelSerializer):
    class Meta:
        model = CompetitionBotMatchupStats
        fields = competition_bot_matchup_stats_include_fields


# !ATTENTION! IF YOU CHANGE THE API ANNOUNCE IT TO USERS

class CompetitionBotMatchupStatsViewSet(viewsets.ReadOnlyModelViewSet):
    """
    CompetitionBotMatchupStats data view
    """
    queryset = CompetitionBotMatchupStats.objects.all()
    serializer_class = CompetitionBotMatchupStatsSerializer

    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = competition_bot_matchup_stats_include_fields
    search_fields = competition_bot_matchup_stats_include_fields
    ordering_fields = competition_bot_matchup_stats_include_fields


# !ATTENTION! IF YOU CHANGE THE API ANNOUNCE IT TO USERS

class CompetitionParticipationSerializer(serializers.ModelSerializer):
    class Meta:
        model = CompetitionParticipation
        fields = competition_participation_include_fields


# !ATTENTION! IF YOU CHANGE THE API ANNOUNCE IT TO USERS

class CompetitionParticipationViewSet(viewsets.ReadOnlyModelViewSet):
    """
    CompetitionParticipation data view
    """
    queryset = CompetitionParticipation.objects.all()
    serializer_class = CompetitionParticipationSerializer

    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = competition_participation_filter_fields
    search_fields = competition_participation_filter_fields
    ordering_fields = competition_participation_filter_fields


# !ATTENTION! IF YOU CHANGE THE API ANNOUNCE IT TO USERS

class DiscordUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = DiscordUser
        fields = discord_user_include_fields


class DiscordUserViewSet(viewsets.ReadOnlyModelViewSet):
    """
    DiscordUser data view
    """
    queryset = DiscordUser.objects.all()
    serializer_class = DiscordUserSerializer
    permission_classes = [IsServiceOrAdminUser]  # Only allow privileged users to access this information

    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = discord_user_include_fields
    search_fields = discord_user_include_fields
    ordering_fields = discord_user_include_fields


# !ATTENTION! IF YOU CHANGE THE API ANNOUNCE IT TO USERS

class GameSerializer(serializers.ModelSerializer):
    class Meta:
        model = Game
        fields = game_include_fields


# !ATTENTION! IF YOU CHANGE THE API ANNOUNCE IT TO USERS

class GameViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Game data view
    """
    queryset = Game.objects.all()
    serializer_class = GameSerializer

    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = game_include_fields
    search_fields = game_include_fields
    ordering_fields = game_include_fields


# !ATTENTION! IF YOU CHANGE THE API ANNOUNCE IT TO USERS

class GameModeSerializer(serializers.ModelSerializer):
    class Meta:
        model = GameMode
        fields = game_mode_include_fields


# !ATTENTION! IF YOU CHANGE THE API ANNOUNCE IT TO USERS

class GameModeViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Game Mode data view
    """
    queryset = GameMode.objects.all()
    serializer_class = GameModeSerializer

    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = game_mode_include_fields
    search_fields = game_mode_include_fields
    ordering_fields = game_mode_include_fields


# !ATTENTION! IF YOU CHANGE THE API ANNOUNCE IT TO USERS

class MapSerializer(serializers.ModelSerializer):
    class Meta:
        model = Map
        fields = map_include_fields
        ref_name = 'website'


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

class MapPoolSerializer(serializers.ModelSerializer):
    class Meta:
        model = MapPool
        fields = map_pool_include_fields


# !ATTENTION! IF YOU CHANGE THE API ANNOUNCE IT TO USERS

class MapPoolViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Map Pool data view
    """
    queryset = MapPool.objects.all()
    serializer_class = MapPoolSerializer

    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = map_pool_include_fields
    search_fields = map_pool_include_fields
    ordering_fields = map_pool_include_fields


# !ATTENTION! IF YOU CHANGE THE API ANNOUNCE IT TO USERS

# This is out of order, because it's used by the MatchSerializer
# todo: bot names are included for the stream to use. Ideally the the stream should properly utilize the API
class ResultSerializer(serializers.ModelSerializer):
    bot1_name = serializers.SerializerMethodField()
    bot2_name = serializers.SerializerMethodField()

    def get_bot1_name(self, obj):
        return obj.match.participants[0].bot.name

    def get_bot2_name(self, obj):
        return obj.match.participants[1].bot.name

    class Meta:
        model = Result
        fields = result_include_fields + ('bot1_name', 'bot2_name')


# !ATTENTION! IF YOU CHANGE THE API ANNOUNCE IT TO USERS

# This is out of order, because it's used by the MatchSerializer
class MatchTagSerializer(serializers.ModelSerializer):
    tag_name = serializers.SerializerMethodField()

    def get_tag_name(self, obj):
        return obj.tag.name

    class Meta:
        model = MatchTag
        fields = matchtag_include_fields + ('tag_name',)


# !ATTENTION! IF YOU CHANGE THE API ANNOUNCE IT TO USERS

class MatchSerializer(serializers.ModelSerializer):
    result = ResultSerializer()
    tags = MatchTagSerializer(many=True)

    class Meta:
        model = Match
        fields = match_include_fields + ('result', 'tags')
        ref_name = 'website'


# !ATTENTION! IF YOU CHANGE THE API ANNOUNCE IT TO USERS

class MatchViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Match data view
    """
    queryset = Match.objects.all().select_related('result',
                                                  'map',
                                                  'assigned_to',
                                                  'requested_by').prefetch_related(
        Prefetch('matchparticipation_set', MatchParticipation.objects.all().select_related('bot'),
                 to_attr='participants'))
    serializer_class = MatchSerializer

    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_class = MatchFilter
    search_fields = match_include_fields
    ordering_fields = match_include_fields


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
    queryset = MatchParticipation.objects.all().select_related('bot', 'bot__user')
    serializer_class = MatchParticipationSerializer

    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_class = MatchParticipationFilter
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

class NewsSerializer(serializers.ModelSerializer):
    class Meta:
        model = News
        fields = news_include_fields


# !ATTENTION! IF YOU CHANGE THE API ANNOUNCE IT TO USERS

class NewsViewSet(viewsets.ReadOnlyModelViewSet):
    """
    News data view
    """
    queryset = News.objects.all()
    serializer_class = NewsSerializer

    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = news_include_fields
    search_fields = news_include_fields
    ordering_fields = news_include_fields


# !ATTENTION! IF YOU CHANGE THE API ANNOUNCE IT TO USERS

class ResultViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Result data view
    """
    queryset = Result.objects.all().select_related('winner').prefetch_related(
        Prefetch('match__matchparticipation_set', MatchParticipation.objects.all().select_related('bot'),
                 to_attr='participants'))
    serializer_class = ResultSerializer

    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_class = ResultFilter
    search_fields = result_search_fields
    ordering_fields = result_search_fields


# !ATTENTION! IF YOU CHANGE THE API ANNOUNCE IT TO USERS

class RoundSerializer(serializers.ModelSerializer):
    class Meta:
        model = Round
        fields = round_include_fields


# !ATTENTION! IF YOU CHANGE THE API ANNOUNCE IT TO USERS

class RoundViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Round data view
    """
    queryset = Round.objects.all()
    serializer_class = RoundSerializer

    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = round_include_fields
    search_fields = round_include_fields
    ordering_fields = round_include_fields


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
