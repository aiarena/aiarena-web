from django.db.models import Prefetch

from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import viewsets
from rest_framework.filters import OrderingFilter, SearchFilter

from aiarena.api.view_filters import ResultFilter
from aiarena.api.views.include import result_search_fields
from aiarena.api.views.serializers import ResultSerializer
from aiarena.core.models import MatchParticipation, Result


class ResultViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Result data view
    """

    queryset = (
        Result.objects.all()
        .select_related("winner")
        .prefetch_related(
            Prefetch(
                "match__matchparticipation_set",
                MatchParticipation.objects.all().select_related("bot"),
                to_attr="participants",
            )
        )
    )
    serializer_class = ResultSerializer

    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_class = ResultFilter
    search_fields = result_search_fields
    ordering_fields = result_search_fields
