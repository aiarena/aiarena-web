from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import viewsets
from rest_framework.filters import OrderingFilter, SearchFilter

from aiarena.api.views.include import news_include_fields
from aiarena.api.views.serializers import NewsSerializer
from aiarena.core.models import News


class NewsViewSet(viewsets.ReadOnlyModelViewSet):
    """
    News data view
    """

    queryset = News.objects.all()
    serializer_class = NewsSerializer

    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = news_include_fields
    search_fields = news_include_fields
    ordering_fields = news_include_fields
