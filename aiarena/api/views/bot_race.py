from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import viewsets
from rest_framework.filters import OrderingFilter, SearchFilter

from aiarena.api.views.include import bot_race_include_fields
from aiarena.api.views.serializers import BotRaceSerializer
from aiarena.core.models.bot_race import BotRace


class BotRaceViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Bot race data view
    """

    queryset = BotRace.objects.all()
    serializer_class = BotRaceSerializer

    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = bot_race_include_fields
    search_fields = bot_race_include_fields
    ordering_fields = bot_race_include_fields
