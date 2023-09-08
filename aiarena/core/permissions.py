from rest_framework.permissions import BasePermission


class IsArenaClientOrAdminUser(BasePermission):
    """
    Allows access to arena clients or admin users.
    """

    def has_permission(self, request, view):
        return bool(
            request.user and request.user.is_authenticated and (request.user.is_arenaclient or request.user.is_staff)
        )


class IsArenaClient(BasePermission):
    """
    Allows access to arena clients.
    """

    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated and request.user.is_arenaclient)


class IsServiceOrAdminUser(BasePermission):
    """
    Allows access to service or admin users.
    """

    def has_permission(self, request, view):
        return bool(
            request.user and request.user.is_authenticated and (request.user.type == "SERVICE" or request.user.is_staff)
        )
