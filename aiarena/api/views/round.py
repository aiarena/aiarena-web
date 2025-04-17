from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import viewsets
from rest_framework.filters import OrderingFilter, SearchFilter

from aiarena.api.views.include import round_include_fields
from aiarena.api.views.serializers import RoundSerializer
from aiarena.core.models import Round


class RoundViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Round data view
    """

    queryset = Round.objects.all()
    serializer_class = RoundSerializer

    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = round_include_fields
    search_fields = round_include_fields
    ordering_fields = round_include_fields
