from django.core.management.base import BaseCommand, CommandError
from django.db import transaction

from aiarena.core.models import User, WebsiteUser


def migrate_website_user(website_user: User):
    # find parent class fields:
    fields = [f.name for f in User._meta.fields]

    # get the values from the user instance
    values = dict([(x, getattr(website_user, x)) for x in fields])

    new_instance = WebsiteUser.objects.create(**values)
    new_instance.save()  # save new one


class Command(BaseCommand):
    help = "Migrates normal django Users to WebsiteUsers."

    def add_arguments(self, parser):
        parser.add_argument("user_ids", nargs="+", type=int, help="A space separated list of user ids to migrate.")

    def handle(self, *args, **options):
        for user_id in options["user_ids"]:
            try:
                with transaction.atomic():
                    user = User.objects.select_for_update().get(pk=user_id)
                    migrate_website_user(user)

                self.stdout.write(self.style.SUCCESS(f'Successfully migrated user "{user_id}"'))
            except User.DoesNotExist:
                raise CommandError(f'User "{user_id}" does not exist')
