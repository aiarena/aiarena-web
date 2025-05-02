from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import viewsets
from rest_framework.filters import OrderingFilter, SearchFilter

from aiarena.api.views.include import map_pool_include_fields
from aiarena.api.views.serializers import MapPoolSerializer
from aiarena.core.models import MapPool


class MapPoolViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Map Pool data view
    """

    queryset = MapPool.objects.all()
    serializer_class = MapPoolSerializer

    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = map_pool_include_fields
    search_fields = map_pool_include_fields
    ordering_fields = map_pool_include_fields
