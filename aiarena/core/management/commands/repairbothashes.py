from django.core.management.base import BaseCommand
from django.db import transaction

from aiarena.core.models import Bot
from aiarena.core.utils import calculate_md5_django_filefield


class Command(BaseCommand):
    help = "Repairs the hashes of bot files which don't match."

    def add_arguments(self, parser):
        parser.add_argument('--zip', action='store_true', help="Repair bot zip file hashes.")
        parser.add_argument('--data', action='store_true', help="Repair bot data file hashes.")

    def handle(self, *args, **options):
        self.stdout.write('Repairing hashes...')

        if options['zip'] is None:
            self.stdout.write('No argument supplied - no actions taken.')
        else:
            for bot in Bot.objects.all():
                with transaction.atomic():
                    bot.lock_me()
                    bot_zip_hash = calculate_md5_django_filefield(bot.bot_zip)
                    if options['zip'] is not None and bot.bot_zip_md5hash != bot_zip_hash:
                        bot.bot_zip_md5hash = bot_zip_hash
                        bot.save()
                        self.stdout.write(f'{bot.name} - bot_zip - MISMATCH - REPAIRED')

                    if options['data'] is not None and bot.bot_data:
                        bot_data_hash = calculate_md5_django_filefield(bot.bot_data)
                        if bot.bot_data_md5hash != bot_data_hash:
                            bot.bot_data_md5hash = bot_data_hash
                            bot.save()
                            self.stdout.write(f'{bot.name} - bot_data - MISMATCH - REPAIRED')

        self.stdout.write('Done.')
