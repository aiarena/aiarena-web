from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import viewsets
from rest_framework.filters import OrderingFilter, SearchFilter

from aiarena.api.views.include import competition_include_fields
from aiarena.api.views.serializers import CompetitionSerializer
from aiarena.core.models import Competition


class CompetitionViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Competition data view
    """

    queryset = Competition.objects.all()
    serializer_class = CompetitionSerializer

    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = competition_include_fields
    search_fields = competition_include_fields
    ordering_fields = competition_include_fields
