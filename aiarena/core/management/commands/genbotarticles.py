from django.core.management.base import BaseCommand, CommandError
from django.db import transaction

from aiarena.core.models import Bot, Match


class Command(BaseCommand):
    help = 'Generates bot articles by saving all bots.'

    def handle(self, *args, **options):
        with transaction.atomic():
            for bot in Bot.objects.all():
                bot.save()

