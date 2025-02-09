from collections.abc import Callable, Iterable
from typing import NamedTuple, Self

from django.utils.functional import SimpleLazyObject, classproperty

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


SCOPE_READ = "read"
SCOPE_WRITE = "write"
SCOPE_DELETE = "delete"


# noinspection PyMethodParameters,PyPep8Naming
class AccessLevel:
    def __init__(self, full: bool = False, scopes: Iterable[str] | None = None):
        self._full = full
        self._scopes = set(scopes or [])

    @classproperty
    def NO_ACCESS(cls: type[Self]) -> "AccessLevel":
        return cls()

    @classproperty
    def READ_ACCESS(cls: type[Self]) -> "AccessLevel":
        return cls(scopes={SCOPE_READ})

    @classproperty
    def WRITE_ACCESS(cls: type[Self]) -> "AccessLevel":
        return cls(scopes={SCOPE_READ, SCOPE_WRITE})

    @classproperty
    def FULL_ACCESS(cls: type[Self]) -> "AccessLevel":
        return cls(full=True)

    def __eq__(self, other: "AccessLevel") -> bool:
        if isinstance(other, AccessLevel):
            return self._full == other._full and self._scopes == other._scopes
        raise NotImplementedError(f"Cannot compare AccessLevel with {other}")

    def add(self, scopes: str | Iterable[str]) -> "AccessLevel":
        if isinstance(scopes, str):
            self._scopes.add(scopes)
        else:
            self._scopes |= set(scopes)
        return self

    def can_delete(self) -> bool:
        return self.can(SCOPE_DELETE)

    def can_read(self) -> bool:
        return self.can(SCOPE_READ)

    def can_write(self) -> bool:
        return self.can(SCOPE_WRITE)

    def can(self, scope: str) -> bool:
        return self._full or scope in self._scopes


class _Checker(NamedTuple):
    user: Callable[..., AccessLevel]


def create_permission_checker() -> _Checker:
    from .models import Bot, User

    def _user_permission(user: User, instance) -> AccessLevel:
        match instance:
            case User():
                if instance == user:
                    return AccessLevel.FULL_ACCESS
            case Bot():
                if instance.user == user:
                    return AccessLevel.FULL_ACCESS

        return AccessLevel.READ_ACCESS

    return _Checker(user=_user_permission)


# noinspection PyTypeChecker
check: _Checker = SimpleLazyObject(create_permission_checker)
