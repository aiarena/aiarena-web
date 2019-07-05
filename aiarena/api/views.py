import logging

from rest_framework import viewsets, serializers

from aiarena.core.models import Match, Result

logger = logging.getLogger(__name__)


class MatchSerializer(serializers.ModelSerializer):
    class Meta:
        model = Match
        fields = 'id', 'created', 'map', 'result'


# todo: make publicly accessible
class MatchViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Match data view
    """
    queryset = Match.objects.all()
    serializer_class = MatchSerializer


class ResultSerializer(serializers.ModelSerializer):
    bot1_name = serializers.SerializerMethodField()
    bot2_name = serializers.SerializerMethodField()

    def get_bot1_name(self, obj):
        return obj.match.participant_set.get(participant_number=1).bot.name

    def get_bot2_name(self, obj):
        return obj.match.participant_set.get(participant_number=2).bot.name

    class Meta:
        model = Result
        fields = 'id', 'created', 'match', 'winner', 'type', 'replay_file', 'duration', 'bot1_name', 'bot2_name'


class ResultViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Result data view
    """
    queryset = Result.objects.all()
    serializer_class = ResultSerializer
