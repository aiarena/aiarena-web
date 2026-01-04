from abc import ABC, abstractmethod


class Supporters(ABC):
    """
    Abstract interface describing supporter-specific limits and permissions.
    """

    @abstractmethod
    def get_active_bots_limit(self, user) -> int | None:
        """Return the maximum number of active bots a user can have.

        Args:
            user: The user for whom the limit is being queried (Django `User`
                  instance or app-specific user object).

        Returns:
            int or None: Maximum number of active bots, or `None` for
            unlimited.
        """
        pass

    @abstractmethod
    def get_requested_matches_limit(self, user) -> int | None:
        """Return the maximum number of periodic requested matches allowed.

        Args:
            user: The user for whom the limit is queried.

        Returns:
            int or None: Maximum number of requested matches allowed, or `None`
            for unlimited.
        """
        pass

    @abstractmethod
    def can_request_match_via_api(self, user) -> bool:
        """Return whether the user is allowed to request matches via the API.

        Args:
            user: The user whose permission is being checked.

        Returns:
            bool: True if the user can request matches via the API, False
                  otherwise.
        """
        pass
