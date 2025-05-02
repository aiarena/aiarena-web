from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import viewsets
from rest_framework.filters import OrderingFilter, SearchFilter

from aiarena.api.views.include import game_include_fields
from aiarena.api.views.serializers import GameSerializer
from aiarena.core.models import Game


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
