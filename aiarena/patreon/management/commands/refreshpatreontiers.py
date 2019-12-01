import traceback

from django.core.management.base import BaseCommand, CommandError

from aiarena.patreon.models import PatreonAccountBind


class Command(BaseCommand):
    help = 'Refreshes all user patreon tiers.'

    def add_arguments(self, parser):
        pass

    def handle(self, *args, **options):
        for patreon_bind in PatreonAccountBind.objects.all():
            try:
                patreon_bind.refresh_token()
                patreon_bind.update_user_patreon_tier()
            except Exception as e:
                raise CommandError(traceback)
