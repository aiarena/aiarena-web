import logging

from .user import User

logger = logging.getLogger(__name__)


class ServiceUser(User):
    """Represents a service user"""

    class Meta:
        verbose_name = 'ServiceUser'
