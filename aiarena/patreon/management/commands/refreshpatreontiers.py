import os
import traceback

from django.core.management.base import BaseCommand, CommandError

from aiarena.core.models import User
from aiarena.patreon.models import PatreonAccountBind


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

        # Sync any users with patreon links
        for patreon_bind in PatreonAccountBind.objects.all():
            try:
                patreon_bind.update_refresh_token()
                patreon_bind.update_user_patreon_tier()
            except Exception as e:
                errors = errors + os.linesep + traceback.format_exc()

        if len(errors) > 0:
            raise CommandError('The following errors occurred:' + errors)
