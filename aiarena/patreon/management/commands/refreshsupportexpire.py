import os
import traceback
from datetime import timedelta, datetime
from pytz import UTC
from django.core.management.base import BaseCommand, CommandError

from aiarena.core.models import User


class Command(BaseCommand):
    help = 'Refreshes supporter status based on expiry date'

    def add_arguments(self, parser):
        pass

    def handle(self, *args, **options):
        now = datetime.astimezone(datetime.now(), tz=UTC)
        for user in User.objects.all():
            if user.supported_expiration_date is not None:
                delta = user.supported_expiration_date - now
                days = delta.days
                if days <=0:
                    user.supported_expiration_date = None
                    user.save()




