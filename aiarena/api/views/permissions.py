from rest_framework import permissions
from rest_framework.permissions import BasePermission


class BotAccessPermission(BasePermission):
    message = "You cannot edit a bot that belongs to someone else"

    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True

        if obj.user != request.user:
            return False

        return True
