from django.db.models import Prefetch

from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import viewsets
from rest_framework.filters import OrderingFilter, SearchFilter

from aiarena.api.view_filters import MatchFilter
from aiarena.api.views.include import match_include_fields
from aiarena.api.views.serializers import MatchSerializer
from aiarena.core.models import Match, MatchParticipation


class MatchViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Match data view
    """

    queryset = (
        Match.objects.all()
        .select_related("result", "map", "assigned_to", "requested_by")
        .prefetch_related(
            Prefetch(
                "matchparticipation_set", MatchParticipation.objects.all().select_related("bot"), to_attr="participants"
            )
        )
    )
    serializer_class = MatchSerializer

    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_class = MatchFilter
    search_fields = match_include_fields
    ordering_fields = match_include_fields
