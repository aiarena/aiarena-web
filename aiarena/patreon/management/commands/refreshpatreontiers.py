import os
import traceback

from django.core.management.base import BaseCommand, CommandError

from aiarena.patreon.models import PatreonAccountBind


class Command(BaseCommand):
    help = 'Refreshes all user patreon tiers.'

    def add_arguments(self, parser):
        pass

    def handle(self, *args, **options):
        errors = ''
        for patreon_bind in PatreonAccountBind.objects.all():
            try:
                patreon_bind.update_refresh_token()
                patreon_bind.update_user_patreon_tier()
            except Exception as e:
                errors = errors + os.linesep + traceback.format_exc()

        if len(errors) > 0:
            raise CommandError('The following errors occurred:' + errors)
