from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import viewsets
from rest_framework.filters import OrderingFilter, SearchFilter

from aiarena.api.views.include import game_mode_include_fields
from aiarena.api.views.serializers import GameModeSerializer
from aiarena.core.models import GameMode


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
