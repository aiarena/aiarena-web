from abc import ABC, abstractmethod

from django.db.models import QuerySet


class Bots(ABC):
    """Interface for bot-related queries and actions.

    Methods are implemented by application code; implementations may perform
    side effects where appropriate (for example, sending notification emails).
    """

    @abstractmethod
    def send_crash_alert(self, bot):
        """Send notification that `bot` crashed/deactivated. Returns None."""
        pass

    @abstractmethod
    def get_active(self) -> QuerySet:
        """Return a QuerySet of active bots."""
        pass

    @abstractmethod
    def get_active_excluding_bot(self, bot):
        """Return active bots excluding `bot` (may raise if none left)."""
        pass

    @abstractmethod
    def get_available(self, bots) -> list:
        """Filter `bots` and return those available for use (not frozen)."""
        pass

    @abstractmethod
    def available_is_more_than(self, bots, amount):
        """Return True if at least `amount` bots from `bots` are available."""
        pass

    @abstractmethod
    def get_random_active(self):
        """Return one random active bot or None if none available."""
        pass

    @abstractmethod
    def get_random_active_bot_excluding(self, id):
        """Return a random active bot excluding `id` (may raise if none left)."""
        pass

    @abstractmethod
    def bot_data_is_frozen(self, bot) -> bool:
        """Return True if `bot`'s data is currently frozen/locked by matches."""
        pass
