from django.core.management.base import BaseCommand

from aiarena import settings
from aiarena.core.models import User
from aiarena.core.utils import EnvironmentType


def purge_user_data():
    for user in User.objects.all():
        user.set_password('x')
        user.email = user.username + '@staging.ai-arena.net'
        user.save()


class Command(BaseCommand):
    help = "Purges sensitive data from the database. Run on production backups."

    def add_arguments(self, parser):
        pass

    def handle(self, *args, **options):

        if settings.ENVIRONMENT_TYPE == EnvironmentType.DEVELOPMENT \
                or settings.ENVIRONMENT_TYPE == EnvironmentType.STAGING:
            purge_user_data()
        else:
            self.stdout.write('Command failed: This is not a development or staging environment!')
