import datetime

from django.conf import settings
from django.core.management import CommandError, call_command
from django.core.management.base import BaseCommand

from aiarena.core.models import WebsiteUser
from aiarena.core.tests.testing_utils import (
    TestingClient,
    create_arena_clients_with_matching_tokens,
    create_bot_for_competition,
    create_game_races,
    create_open_competition_with_map,
)


class Command(BaseCommand):
    """
    This command is intended for use alongside the integration tests found at /aiarena/api/arenaclient/integration_tests
    """

    help = "A convenience command to seed the database with initial data for arena client integration tests."

    _DEFAULT_ARENACLIENTS_TO_GENERATE = 10

    def add_arguments(self, parser):
        parser.add_argument(
            "--numacs",
            type=int,
            default=self._DEFAULT_ARENACLIENTS_TO_GENERATE,
            help=(
                f"Number of Arena Clients to generate. "
                f"Default is {self._DEFAULT_ARENACLIENTS_TO_GENERATE}. MUST be at least 1."
            ),
        )

    def handle(self, *args, **options):
        if settings.ENVIRONMENT_TYPE != settings.ENVIRONMENT_TYPES.DEVELOPMENT:
            raise CommandError("Integration test seeding failed: This is not a development environment!")

        started_at = datetime.datetime.now()
        self.stdout.write(f"Started at: {started_at}")

        self.stdout.write("Migrating database...")
        call_command("migrate", "--noinput")
        self.stdout.write("Flushing data...")
        call_command("flush", "--noinput")

        self.stdout.write("Seeding data...")

        num_acs = options["numacs"]

        devadmin = WebsiteUser.objects.create_superuser(
            username="devadmin", password="x", email="devadmin@dev.aiarena.net"
        )

        client = TestingClient()
        client.login(devadmin)

        create_arena_clients_with_matching_tokens(self.stdout, client, num_acs, devadmin)

        game = client.create_game("StarCraft II")
        gamemode = client.create_gamemode("Melee", game.id)

        competition = create_open_competition_with_map(
            client,
            "Competition 1",
            "L",
            gamemode.id,
            target_n_divisions=2,
            target_division_size=2,
            n_placements=2,
            rounds_per_cycle=1,
            indepth_bot_statistics_enabled=True,
        )

        protoss, terran, zerg = create_game_races()

        num_bots_to_create = num_acs * 2  # 2 bots per arena client
        self.create_bots_for_competition(competition, devadmin, terran, num_bots_to_create)

        self.stdout.write('Done. User logins have a password of "x".')
        self.stdout.write('AC API Tokens have been set to their AC number e.g. arenaclient-1\'s token is "1"')
        finished_at = datetime.datetime.now()
        self.stdout.write(f"Finished at: {finished_at}")
        self.stdout.write(f"Elapsed seconds: {(finished_at - started_at).total_seconds()}")

    def create_bots_for_competition(self, competition, for_user, race, num_bots):
        for i in range(num_bots):
            create_bot_for_competition(competition, for_user, f"devadmin_bot{i}", "python", race)
