import os
import traceback

from constance import config
from django.core.management.base import BaseCommand, CommandError

from aiarena.core.models import User
from aiarena.patreon.models import PatreonAccountBind
from aiarena.patreon.patreon import PatreonOAuth, update_unlinked_discord_users


class Command(BaseCommand):
    help = 'Refreshes all user patreon tiers.'

    def add_arguments(self, parser):
        pass

    def handle(self, *args, **options):
        errors = ''

        # Wipe existing patreon levels that are set to sync but aren't linked to patreon
        for user in User.objects.filter(patreonaccountbind__isnull=True, sync_patreon_status=True).exclude(patreon_level='none'):
            user.patreon_level = 'none'
            user.save()

        # Sync any users with patreon links that are set to sync
        for patreon_bind in PatreonAccountBind.objects.filter(user__sync_patreon_status=True):
            try:
                patreon_bind.update_tokens()
                patreon_bind.update_user_patreon_tier()
            except Exception as e:
                errors = errors + os.linesep + traceback.format_exc()

        update_unlinked_discord_users()

        if len(errors) > 0:
            raise CommandError('The following errors occurred:' + errors)
