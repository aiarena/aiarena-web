import os
import traceback

from django.core.management.base import BaseCommand, CommandError

from aiarena.core.models import User


class Command(BaseCommand):
    help = 'Refreshes supporter status based on expiry date'

    def add_arguments(self, parser):
        pass

    def handle(self, *args, **options):

        for user in User.objects.all():
            if user.supported_expiration_date is not None:
                # TODO some code to assert the date is in the future
                # if the date is in the past , present
                # turn user.supported_expiration_date back to None
                # TODO Test this
                user.save()


