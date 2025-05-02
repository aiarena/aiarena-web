from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import viewsets
from rest_framework.filters import OrderingFilter, SearchFilter

from aiarena.api.views.include import competition_bot_matchup_stats_include_fields
from aiarena.api.views.serializers import CompetitionBotMatchupStatsSerializer
from aiarena.core.models import CompetitionBotMatchupStats


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
