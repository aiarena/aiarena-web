from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import viewsets
from rest_framework.filters import OrderingFilter, SearchFilter

from aiarena.api.views.include import discord_user_include_fields
from aiarena.api.views.serializers import DiscordUserSerializer
from aiarena.core.permissions import IsServiceOrAdminUser
from discord_bind.models import DiscordUser


class DiscordUserViewSet(viewsets.ReadOnlyModelViewSet):
    """
    DiscordUser data view
    """

    queryset = DiscordUser.objects.all()
    serializer_class = DiscordUserSerializer
    permission_classes = [IsServiceOrAdminUser]  # Only allow privileged users to access this information

    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = discord_user_include_fields
    search_fields = discord_user_include_fields
    ordering_fields = discord_user_include_fields
