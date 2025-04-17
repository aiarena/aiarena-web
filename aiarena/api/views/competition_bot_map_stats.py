from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import viewsets
from rest_framework.filters import OrderingFilter, SearchFilter

from aiarena.api.views.include import competition_bot_map_stats_include_fields
from aiarena.api.views.serializers import CompetitionBotMapStatsSerializer
from aiarena.core.models import CompetitionBotMapStats


class CompetitionBotMapStatsViewSet(viewsets.ReadOnlyModelViewSet):
    """
    CompetitionBotMapStats data view
    """

    queryset = CompetitionBotMapStats.objects.all()
    serializer_class = CompetitionBotMapStatsSerializer

    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = competition_bot_map_stats_include_fields
    search_fields = competition_bot_map_stats_include_fields
    ordering_fields = competition_bot_map_stats_include_fields
