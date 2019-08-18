import logging

from rest_framework import viewsets, serializers

from aiarena.core.models import Match, Result, Bot, Map, User, Round, Participant

logger = logging.getLogger(__name__)


class BotSerializer(serializers.ModelSerializer):
    class Meta:
        model = Bot
        exclude = 'bot_zip', 'bot_zip_md5hash', 'bot_zip_publicly_downloadable', \
                  'bot_data', 'bot_data_md5hash', 'bot_data_publicly_downloadable'


class BotViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Bot data view
    """
    queryset = Bot.objects.all()
    serializer_class = BotSerializer


class MapSerializer(serializers.ModelSerializer):
    class Meta:
        model = Map
        # todo: The file isn't used by the arena clients currently, so exclude it to avoid confusion.
        # todo: Eventually the arena clients will download maps from the website
        exclude = 'file',


class MapViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Map data view
    """
    queryset = Map.objects.all()
    serializer_class = MapSerializer


class MatchSerializer(serializers.ModelSerializer):
    class Meta:
        model = Match
        fields = '__all__'


class MatchViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Match data view
    """
    queryset = Match.objects.all()
    serializer_class = MatchSerializer


class ParticipantSerializer(serializers.ModelSerializer):
    class Meta:
        model = Participant
        fields = '__all__'


class ParticipantViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Result data view
    """
    queryset = Participant.objects.all()
    serializer_class = ParticipantSerializer


class ResultSerializer(serializers.ModelSerializer):
    class Meta:
        model = Result
        fields = '__all__'


class ResultViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Result data view
    """
    queryset = Result.objects.all()
    serializer_class = ResultSerializer


class RoundSerializer(serializers.ModelSerializer):
    class Meta:
        model = Round
        fields = '__all__'


class RoundViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Result data view
    """
    queryset = Round.objects.all()
    serializer_class = RoundSerializer


class UserSerializer(serializers.ModelSerializer):
    name = serializers.CharField(source='username')

    class Meta:
        model = User
        fields = 'id', 'name', 'service_account'


class UserViewSet(viewsets.ReadOnlyModelViewSet):
    """
    User data view
    """
    queryset = User.objects.filter(is_active=True)
    serializer_class = UserSerializer
