from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import viewsets
from rest_framework.filters import OrderingFilter, SearchFilter

from aiarena.api.views.include import user_include_fields
from aiarena.api.views.serializers import UserSerializer
from aiarena.core.models import User


class UserViewSet(viewsets.ReadOnlyModelViewSet):
    """
    User data view
    """

    queryset = User.objects.all()
    serializer_class = UserSerializer

    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = user_include_fields
    search_fields = user_include_fields
    ordering_fields = user_include_fields
