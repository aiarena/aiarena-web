from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import viewsets
from rest_framework.filters import OrderingFilter, SearchFilter

from aiarena.api.views.include import competition_participation_filter_fields
from aiarena.api.views.serializers import CompetitionParticipationSerializer
from aiarena.core.models import CompetitionParticipation


class CompetitionParticipationViewSet(viewsets.ReadOnlyModelViewSet):
    """
    CompetitionParticipation data view
    """

    queryset = CompetitionParticipation.objects.all()
    serializer_class = CompetitionParticipationSerializer

    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = competition_participation_filter_fields
    search_fields = competition_participation_filter_fields
    ordering_fields = competition_participation_filter_fields
