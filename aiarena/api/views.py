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
    Public MatchViewSet for viewing match data
    """
    queryset = Match.objects.all()
    serializer_class = MatchSerializer


class ResultSerializer(serializers.ModelSerializer):
    class Meta:
        model = Result
        fields = 'id', 'created', 'match', 'winner', 'type', 'replay_file', 'duration'


class ResultViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Public MatchViewSet for viewing match data
    """
    queryset = Result.objects.all()
    serializer_class = ResultSerializer
