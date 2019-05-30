import logging

from rest_framework import viewsets, serializers

from aiarena.core.models import Match, Result

logger = logging.getLogger(__name__)


class ResultSerializer(serializers.ModelSerializer):
    class Meta:
        model = Result
        fields = 'id', 'created', 'winner', 'type', 'replay_file', 'duration'


class MatchSerializer(serializers.ModelSerializer):
    result = ResultSerializer()

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
