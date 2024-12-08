import datetime
import random

from django.conf import settings
from django.core.files import File
from django.core.management import call_command
from django.core.management.base import BaseCommand

from rest_framework.authtoken.models import Token

from aiarena.api.arenaclient.testing_utils import AcApiTestingClient
from aiarena.core.models import Bot, CompetitionParticipation, Map, MapPool, News, WebsiteUser
from aiarena.core.tests.testing_utils import TestingClient, create_arena_clients_with_matching_tokens, create_game_races
from aiarena.core.tests.tests import TestAssetPaths


class Command(BaseCommand):
    help = "Seed database for testing and development."

    _DEFAULT_MATCHES_TO_GENERATE = 50
    _DEFAULT_ARENACLIENTS_TO_GENERATE = 2

    def add_arguments(self, parser):
        parser.add_argument(
            "--matches",
            type=int,
            default=self._DEFAULT_MATCHES_TO_GENERATE,
            help=f"Number of matches to generate. Default is {self._DEFAULT_MATCHES_TO_GENERATE}.",
        )
        parser.add_argument(
            "--numacs",
            type=int,
            default=self._DEFAULT_ARENACLIENTS_TO_GENERATE,
            help=(
                f"Number of Arena Clients to generate. "
                f"Default is {self._DEFAULT_ARENACLIENTS_TO_GENERATE}. MUST be at least 1."
            ),
        )
        parser.add_argument("--flush", action="store_true", help="Whether to flush the existing database data.")
        parser.add_argument("--migrate", action="store_true", help="Whether to migrate the database first.")
        parser.add_argument("--randomseed", type=int, help="Set the random seed. Useful for consistent test results.")

    def handle(self, *args, **options):
        if settings.ENVIRONMENT_TYPE == settings.ENVIRONMENT_TYPES.DEVELOPMENT:
            started_at = datetime.datetime.now()
            self.stdout.write(f"Started at: {started_at}")
            if options["randomseed"] is not None:
                random_seed = options["randomseed"]
                self.stdout.write(f"Setting random seed to {random_seed}")
                random.seed(random_seed)
            if options["migrate"] is not None:
                self.stdout.write("Migrating database...")
                call_command("migrate", "--noinput")

            if options["flush"] is not None:
                self.stdout.write("Flushing data...")
                call_command("flush", "--noinput")

            self.stdout.write("Seeding data...")

            self.stdout.write(f"Generating {options['matches']} match(es)...")
            self.run_seed(options["numacs"], options["matches"])

            self.stdout.write("Creating news items...")
            News.objects.create(title="News item 1", text="This is news item number 1!")
            News.objects.create(
                title="News item 2",
                text="This is news item number 2! Lets add some text to make it longer. "
                "Evening longer still! Lets make it so long that it hopefully exposes any issues "
                "in our testing. Maybe formatting errors, or something like that. "
                "Now lets repeat everything because I'm too lazy to think of any more to say. "
                "This is news item number 1! Lets add some text to make it longer. "
                "Evening longer still! Lets make it so long that it hopefully exposes any issues "
                "in our testing. Maybe formatting errors, or something like that. ",
            )

            self.stdout.write('Done. User logins have a password of "x".')
            self.stdout.write('AC API Tokens have been set to their AC number e.g. arenaclient-1\'s token is "1"')
            finished_at = datetime.datetime.now()
            self.stdout.write(f"Finished at: {finished_at}")
            self.stdout.write(f"Elapsed seconds: {(finished_at - started_at).total_seconds()}")
        else:
            self.stdout.write("Seeding failed: This is not a development or staging environment!")

    def run_seed(self, num_acs: int, matches):
        self.stdout.write("Seeding initial website data...")

        devadmin = WebsiteUser.objects.create_superuser(
            username="devadmin", password="x", email="devadmin@dev.aiarena.net"
        )

        client = TestingClient()
        client.login(devadmin)

        create_arena_clients_with_matching_tokens(self.stdout, client, num_acs, devadmin)

        client.create_user("service_user", "x", "service_user@dev.aiarena.net", "SERVICE", devadmin.id)

        ac_client = AcApiTestingClient(api_token=Token.objects.first().key)

        game = client.create_game("StarCraft II", ".SC2Map")
        gamemode = client.create_gamemode("Melee", game.id)

        protoss, terran, zerg = create_game_races()

        competition1, competition2, competition3 = self.create_open_competitions(client, gamemode, terran)
        self.create_competition_maps(competition1, competition2, competition3, gamemode)

        devuser1, devuser2, devuser3, devuser4, devuser5 = self.create_5_website_users()

        self.create_bots(
            competition1,
            competition2,
            competition3,
            devadmin,
            devuser1,
            devuser2,
            devuser3,
            devuser4,
            devuser5,
            protoss,
            terran,
            zerg,
        )

        self.run_matches(ac_client, matches)

        self.create_newly_joining_bots(competition1, devadmin, terran)

    def create_newly_joining_bots(self, competition1, devadmin, terran):
        """
        Create bots that have just joined the competition1
        """
        with open(TestAssetPaths.test_bot_zip_path, "rb") as bot_zip:
            # bot still in placement
            bot = Bot.objects.create(
                user=devadmin, name="devadmin_bot100", plays_race=terran, type="python", bot_zip=File(bot_zip)
            )
            cp = CompetitionParticipation.objects.create(competition=competition1, bot=bot)
            competition1.refresh_from_db()
            cp.division_num = competition1.n_divisions
            cp.save()
        with open(TestAssetPaths.test_bot_zip_path, "rb") as bot_zip:
            # bot that just joined the competition
            bot = Bot.objects.create(
                user=devadmin, name="devadmin_bot101", plays_race=terran, type="python", bot_zip=File(bot_zip)
            )
            CompetitionParticipation.objects.create(competition=competition1, bot=bot)

    def run_matches(self, ac_client, matches):
        count = 0
        for x in range(matches - 1):
            self.stdout.write(f"Running matches...{count / matches * 100}%", ending="\r")
            match = ac_client.next_match()

            # Every 20 games, player 1 and 2 alternate crashes
            if x % 40 == 0:
                result_type = "Player1Crash"
            elif x % 20 == 0:
                result_type = "Player2Crash"
            elif x % 50 == 0:
                # Every 50 games, a tie occurs.
                result_type = "Tie"
            else:
                # Alternate wins between player 1 and 2.
                result_type = "Player1Win" if x % 2 == 0 else "Player2Win"
            ac_client.submit_result(match.id, result_type)

            if x == 0:  # make it so a bot that once was active, is now inactive
                bot1 = CompetitionParticipation.objects.filter(active=True).first()
                bot1.active = False
                bot1.save()

            count += 1
        self.stdout.write("Running matches...100%")
        # so we have a match in progress
        if matches != 0:
            ac_client.next_match()

    def create_bots(
        self,
        competition1,
        competition2,
        competition3,
        devadmin,
        devuser1,
        devuser2,
        devuser3,
        devuser4,
        devuser5,
        protoss,
        terran,
        zerg,
    ):
        with open(TestAssetPaths.test_bot_zip_path, "rb") as bot_zip:
            bot = Bot.objects.create(
                user=devadmin, name="devadmin_bot1", plays_race=terran, type="python", bot_zip=File(bot_zip)
            )
            CompetitionParticipation.objects.create(competition=competition1, bot=bot)
            CompetitionParticipation.objects.create(competition=competition2, bot=bot)
            CompetitionParticipation.objects.create(competition=competition3, bot=bot)
        with open(TestAssetPaths.test_bot_zip_path, "rb") as bot_zip:
            bot = Bot.objects.create(
                user=devadmin, name="devadmin_bot2", plays_race=zerg, type="python", bot_zip=File(bot_zip)
            )
            CompetitionParticipation.objects.create(competition=competition2, bot=bot)
        with open(TestAssetPaths.test_bot_zip_path, "rb") as bot_zip:
            Bot.objects.create(
                user=devadmin, name="devadmin_bot3", plays_race=protoss, type="python", bot_zip=File(bot_zip)
            )  # inactive bot
        with open(TestAssetPaths.test_bot_zip_path, "rb") as bot_zip:
            bot = Bot.objects.create(
                user=devuser1, name="devuser1_bot1", plays_race=protoss, type="python", bot_zip=File(bot_zip)
            )
            CompetitionParticipation.objects.create(competition=competition1, bot=bot)
            CompetitionParticipation.objects.create(competition=competition2, bot=bot)
        with open(TestAssetPaths.test_bot_zip_path, "rb") as bot_zip:
            bot = Bot.objects.create(
                user=devuser1, name="devuser1_bot2", plays_race=zerg, type="python", bot_zip=File(bot_zip)
            )
            CompetitionParticipation.objects.create(competition=competition1, bot=bot)
        with open(TestAssetPaths.test_bot_zip_path, "rb") as bot_zip:
            Bot.objects.create(
                user=devuser1, name="devuser1_bot3", plays_race=terran, type="python", bot_zip=File(bot_zip)
            )  # inactive bot
        with open(TestAssetPaths.test_bot_zip_path, "rb") as bot_zip:
            bot = Bot.objects.create(
                user=devuser2, name="devuser2_bot1", plays_race=protoss, type="python", bot_zip=File(bot_zip)
            )
            CompetitionParticipation.objects.create(competition=competition1, bot=bot)
        with open(TestAssetPaths.test_bot_zip_path, "rb") as bot_zip:
            bot = Bot.objects.create(
                user=devuser2, name="devuser2_bot2", plays_race=terran, type="python", bot_zip=File(bot_zip)
            )
            CompetitionParticipation.objects.create(competition=competition1, bot=bot)
            CompetitionParticipation.objects.create(competition=competition3, bot=bot)
        with open(TestAssetPaths.test_bot_zip_path, "rb") as bot_zip:
            Bot.objects.create(
                user=devuser2, name="devuser2_bot3", plays_race=zerg, type="python", bot_zip=File(bot_zip)
            )  # inactive bot
        with open(TestAssetPaths.test_bot_zip_path, "rb") as bot_zip:
            bot = Bot.objects.create(
                user=devuser3, name="devuser3_bot1", plays_race=terran, type="python", bot_zip=File(bot_zip)
            )
            CompetitionParticipation.objects.create(competition=competition1, bot=bot)
        with open(TestAssetPaths.test_bot_zip_path, "rb") as bot_zip:
            bot = Bot.objects.create(
                user=devuser4, name="devuser4_bot1", plays_race=zerg, type="python", bot_zip=File(bot_zip)
            )
            CompetitionParticipation.objects.create(competition=competition2, bot=bot)
        with open(TestAssetPaths.test_bot_zip_path, "rb") as bot_zip:
            bot = Bot.objects.create(
                user=devuser5, name="devuser5_bot1", plays_race=protoss, type="python", bot_zip=File(bot_zip)
            )
            CompetitionParticipation.objects.create(competition=competition1, bot=bot)
            CompetitionParticipation.objects.create(competition=competition2, bot=bot)

    def create_5_website_users(self):
        devuser1 = WebsiteUser.objects.create_user(
            username="devuser1", password="x", email="devuser1@dev.aiarena.net", patreon_level="bronze"
        )
        devuser2 = WebsiteUser.objects.create_user(
            username="devuser2", password="x", email="devuser2@dev.aiarena.net", patreon_level="silver"
        )
        devuser3 = WebsiteUser.objects.create_user(
            username="devuser3", password="x", email="devuser3@dev.aiarena.net", patreon_level="gold"
        )
        devuser4 = WebsiteUser.objects.create_user(
            username="devuser4", password="x", email="devuser4@dev.aiarena.net", patreon_level="platinum"
        )
        devuser5 = WebsiteUser.objects.create_user(
            username="devuser5", password="x", email="devuser5@dev.aiarena.net", patreon_level="diamond"
        )
        return devuser1, devuser2, devuser3, devuser4, devuser5

    def create_competition_maps(self, competition1, competition2, competition3, gamemode):
        with open(TestAssetPaths.test_map_path, "rb") as map:
            m1 = Map.objects.create(name="test_map1", file=File(map), game_mode=gamemode)
            m1.competitions.add(competition1)
            m1.competitions.add(competition2)
            m1.save()
        with open(TestAssetPaths.test_map_path, "rb") as map:
            m2 = Map.objects.create(name="test_map2_terran_only", file=File(map), game_mode=gamemode)
            m2.competitions.add(competition3)
            m2.save()
        with open(TestAssetPaths.test_map_path, "rb") as map:
            # unused map
            Map.objects.create(name="test_map3", file=File(map), game_mode=gamemode)
        map_pool = MapPool.objects.create(name="test_map_pool")
        map_pool.maps.add(m1)
        map_pool.maps.add(m2)

    def create_open_competitions(self, client, gamemode, terran):
        competition1 = client.create_competition(
            "Competition 1",
            "L",
            gamemode.id,
            target_n_divisions=2,
            target_division_size=2,
            n_placements=2,
            rounds_per_cycle=1,
            indepth_bot_statistics_enabled=True,
        )
        client.open_competition(competition1.id)
        competition2 = client.create_competition("Competition 2", "L", gamemode.id, indepth_bot_statistics_enabled=True)
        client.open_competition(competition2.id)
        competition3 = client.create_competition("Competition 3 - Terran Only", "L", gamemode.id, {terran.id})
        client.open_competition(competition3.id)
        return competition1, competition2, competition3
