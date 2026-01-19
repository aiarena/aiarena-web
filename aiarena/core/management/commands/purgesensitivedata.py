from django.conf import settings
from django.core.management.base import BaseCommand

from aiarena.core.models import User
from aiarena.patreon.models import PatreonAccountBind
from discord_bind.models import DiscordInvite, DiscordUser


def purge_user_data():
    for user in User.objects.all():
        user.email = user.username + "@staging.aiarena.net"
        user.save()

    # discord integration
    DiscordUser.objects.all().delete()
    DiscordInvite.objects.all().delete()

    # patreon integration
    PatreonAccountBind.objects.all().delete()


class Command(BaseCommand):
    help = "Purges sensitive data from the database. Run on production backups."

    def add_arguments(self, parser):
        pass

    def handle(self, *args, **options):
        if settings.ENVIRONMENT_TYPE == settings.ENVIRONMENT_TYPES.DEVELOPMENT:
            purge_user_data()
        else:
            self.stdout.write("Command failed: This is not a development or staging environment!")
