from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import viewsets
from rest_framework.filters import OrderingFilter, SearchFilter

from aiarena.api.views.include import patreon_unlinked_uid_include_fields
from aiarena.api.views.serializers import PatreonUnlinkedDiscordUIDSerializer
from aiarena.core.permissions import IsServiceOrAdminUser
from aiarena.patreon.models import PatreonUnlinkedDiscordUID


class PatreonUnlinkedDiscordUIDViewSet(viewsets.ReadOnlyModelViewSet):
    """
    PatreonUnlinkedDiscordUID data view
    """

    queryset = PatreonUnlinkedDiscordUID.objects.all()
    serializer_class = PatreonUnlinkedDiscordUIDSerializer
    permission_classes = [IsServiceOrAdminUser]  # Only allow privileged users to access this information

    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = patreon_unlinked_uid_include_fields
    search_fields = patreon_unlinked_uid_include_fields
    ordering_fields = patreon_unlinked_uid_include_fields
