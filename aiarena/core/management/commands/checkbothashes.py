from datetime import timedelta

from django.core.management.base import BaseCommand
from django.db import transaction
from django.utils import timezone

from aiarena.core.models import Result, Bot
from aiarena.core.utils import calculate_md5_django_filefield


class Command(BaseCommand):
    help = "Check all bot files against their database hashes."

    def handle(self, *args, **options):
        self.stdout.write("Checking hashes...")
        for bot in Bot.objects.all():
            if bot.bot_zip_md5hash == calculate_md5_django_filefield(bot.bot_zip):
                self.stdout.write(f"{bot.name} - bot_zip - MATCH")
            else:
                self.stdout.write(f"{bot.name} - bot_zip - MISMATCH")

            if bot.bot_data:
                if bot.bot_data_md5hash == calculate_md5_django_filefield(bot.bot_data):
                    self.stdout.write(f"{bot.name} - bot_data - MATCH")
                else:
                    self.stdout.write(f"{bot.name} - bot_data - MISMATCH")

        self.stdout.write("Done.")
