from rest_framework.permissions import BasePermission


class IsArenaClient(BasePermission):
    """
    Allows access only to arena clients.
    """

    def has_permission(self, request, view):
        return bool(request.user and request.user.user_type == 'ARENA_CLIENT')
