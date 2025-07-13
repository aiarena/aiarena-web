import logging

from django.contrib.auth.models import AbstractUser
from django.db import models
from django.db.models.signals import pre_save
from django.dispatch import receiver
from django.utils import timezone
from django.utils.functional import cached_property
from django.utils.html import escape
from django.utils.safestring import mark_safe
from django.utils.translation import gettext_lazy as _

from aiarena.core.models.mixins import LockableModelMixin
from aiarena.frontend.templatetags.url_utils import get_absolute_url


logger = logging.getLogger(__name__)


class User(AbstractUser, LockableModelMixin):
    PATREON_LEVELS = (
        ("none", "None"),
        ("bronze", "Bronze"),
        ("silver", "Silver"),
        ("gold", "Gold"),
        ("platinum", "Platinum"),
        ("diamond", "Diamond"),
    )
    USER_TYPES = (
        # When adding types here, ensure they are considered in post_save and validate_user_owner
        ("WEBSITE_USER", "Website User"),
        ("ARENA_CLIENT", "Arena Client"),
        ("SERVICE", "Service"),
    )
    date_joined = models.DateTimeField(_("date joined"), default=timezone.now, blank=True)
    email = models.EmailField(unique=True)
    patreon_level = models.CharField(max_length=16, choices=PATREON_LEVELS, default="none", blank=True)
    type = models.CharField(max_length=16, choices=USER_TYPES, default="WEBSITE_USER", blank=True)
    extra_active_competition_participations = models.IntegerField(default=0, blank=True)
    extra_periodic_match_requests = models.IntegerField(default=0, blank=True)
    receive_email_comms = models.BooleanField(default=True, blank=True)
    sync_patreon_status = models.BooleanField(default=True, blank=True)
    note = models.TextField(blank=True, null=True)

    @cached_property
    def as_truncated_html_link(self):
        name = escape(self.__str__())
        limit = 20

        if self.type == "WEBSITE_USER":
            viewname = "author"
        elif self.type == "ARENA_CLIENT":
            viewname = "arenaclient"
        else:
            raise Exception("This user type does not have a url.")

        return mark_safe(
            f'<a href="{get_absolute_url(viewname, self)}">{(name[:limit-3] + "...") if len(name) > limit else name}</a>'
        )

    @property
    def has_donated(self):
        """
        Whether the user has donated funds to the project.
        """
        return self.patreon_level != "none"

    @property
    def is_supporter(self):
        """
        In future this will include logic for determining general support - not just financial.
        """
        return self.has_donated

    @staticmethod
    def random_supporter():
        # todo: apparently order_by('?') is really slow
        # https://stackoverflow.com/questions/962619/how-to-pull-a-random-record-using-djangos-orm#answer-962672
        return User.objects.only("id", "username", "type").exclude(patreon_level="none").order_by("?").first()

    @property
    def is_arenaclient(self):
        from .arena_client import ArenaClient  # avoid circular reference

        try:
            return self.arenaclient is not None
        except ArenaClient.DoesNotExist:
            return False

    @property
    def is_websiteuser(self):
        from .website_user import WebsiteUser  # avoid circular reference

        try:
            return self.websiteuser is not None
        except WebsiteUser.DoesNotExist:
            return False

    def permission(self, instance):
        from .. import permissions

        return permissions.check.user(user=self, instance=instance)


# Don't allow non WebsiteUsers to login to the website.
@receiver(pre_save, sender=User)
def pre_save_user(sender, instance, **kwargs):
    if not instance.is_websiteuser:
        instance.set_unusable_password()
