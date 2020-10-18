import os
import traceback
from datetime import datetime

from django.core.management.base import BaseCommand, CommandError
from pytz import UTC

from aiarena.core.models import User
from aiarena.patreon.models import PatreonAccountBind


class Command(BaseCommand):
    help = 'Refreshes all user Support tiers.'

    def add_arguments(self, parser):
        pass

    @staticmethod
    def custom_supporter_sync():
        # Custom Supporters sync
        now = datetime.astimezone(datetime.now(), tz=UTC)
        for user in User.objects.all():
            if user.supported_expiration_date is not None:
                delta = user.supported_expiration_date - now
                days = delta.days
                if days <= 0:
                    user.supported_expiration_date = None
                    # remove the tier, since it expired
                    user.supporter_level = 'none'
                    user.save()

    def handle(self, *args, **options):
        errors = ''

        # Wipe existing patreon levels that are set to sync but aren't linked to patreon
        for user in User.objects.filter(patreonaccountbind__isnull=True, sync_patreon_status=True).exclude(supporter_level='none'):
            # if user is not patreon, but a custom supporter
            if not user.supported_expiration_date:
                user.supporter_level = 'none'
                user.save()

        # Sync any users with patreon links
        for patreon_bind in PatreonAccountBind.objects.all():
            try:
                patreon_bind.update_refresh_token()
                patreon_bind.update_user_support_tier()
            except Exception as e:
                errors = errors + os.linesep + traceback.format_exc()

        self.custom_supporter_sync()

        if len(errors) > 0:
            raise CommandError('The following errors occurred:' + errors)
