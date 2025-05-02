from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import viewsets
from rest_framework.filters import OrderingFilter, SearchFilter

from aiarena.api.views.include import map_filter_fields
from aiarena.api.views.serializers import MapSerializer
from aiarena.core.models import Map


class MapViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Map data view
    """

    queryset = Map.objects.all()
    serializer_class = MapSerializer

    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = map_filter_fields
    search_fields = map_filter_fields
    ordering_fields = map_filter_fields
