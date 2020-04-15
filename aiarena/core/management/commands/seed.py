import random

from django.core.files import File
from django.core.management import call_command
from django.core.management.base import BaseCommand
from django.db import transaction
from rest_framework.authtoken.models import Token

from aiarena import settings
from aiarena.core.models import User, Map, Bot, Result, MatchParticipation, Season, Match
from aiarena.core.tests.tests import BaseTestMixin
from aiarena.core.utils import EnvironmentType
from aiarena.core.api import Matches


def create_match(as_user):
    return Matches.start_next_match(as_user)


def create_result_with_bot_data_and_logs(match, type, as_user):
    with open(BaseTestMixin.test_replay_path, 'rb') as result_replay, \
            open(BaseTestMixin.test_bot1_data_path, 'rb') as bot1_data, \
            open(BaseTestMixin.test_bot2_data_path, 'rb') as bot2_data, \
            open(BaseTestMixin.test_bot1_match_log_path, 'rb') as bot1_log, \
            open(BaseTestMixin.test_bot2_match_log_path, 'rb') as bot2_log:
        result = Result.objects.create(match=match, type=type, replay_file=File(result_replay), game_steps=1,
                                       submitted_by=as_user)
        p1 = MatchParticipation.objects.get(match_id=result.match_id, participant_number=1)
        p1.avg_step_time = 0.111111
        p1.match_log = File(bot1_log)
        p1.save()

        p2 = MatchParticipation.objects.get(match_id=result.match_id, participant_number=2)
        p2.avg_step_time = 0.222222
        p2.match_log = File(bot2_log)
        p1.save()

        bot1 = Bot.objects.get(pk=p1.bot_id)
        bot1.bot_data = File(bot1_data)
        bot1.save()

        bot2 = Bot.objects.get(pk=p2.bot_id)
        bot2.bot_data = File(bot2_data)
        bot2.save()

        finalize_result(result, p1, p2, bot1, bot2)


def create_result(match, type, as_user):
    with open(BaseTestMixin.test_replay_path, 'rb') as result_replay:
        result = Result.objects.create(match=match, type=type, replay_file=File(result_replay), game_steps=1,
                                       submitted_by=as_user)
        p1 = MatchParticipation.objects.get(match_id=result.match_id, participant_number=1)
        p1.avg_step_time = 0.111111
        p1.match_log = None
        p1.save()

        p2 = MatchParticipation.objects.get(match_id=result.match_id, participant_number=2)
        p2.avg_step_time = 0.222222
        p2.match_log = None
        p1.save()

        bot1 = Bot.objects.get(pk=p1.bot_id)
        bot1.bot_data = None
        bot1.save()

        bot2 = Bot.objects.get(pk=p2.bot_id)
        bot2.bot_data = None
        bot2.save()

        finalize_result(result, p1, p2, bot1, bot2)


@transaction.atomic
def finalize_result(result, p1, p2, bot1, bot2):
    # imitates the arenaclient result view

    bot1.leave_match(result.match_id)
    bot2.leave_match(result.match_id)

    # Update and record ELO figures
    p1_initial_elo, p2_initial_elo = result.get_initial_elos()
    result.adjust_elo()

    # Calculate the change in ELO
    # the bot elos have changed so refresh them
    # todo: instead of having to refresh, return data from adjust_elo and apply it here
    sp1, sp2 = result.get_season_participants()
    p1.resultant_elo = sp1.elo
    p2.resultant_elo = sp2.elo
    p1.elo_change = p1.resultant_elo - p1_initial_elo
    p2.elo_change = p2.resultant_elo - p2_initial_elo
    p1.save()
    p2.save()

    result.match.round.update_if_completed()


def run_seed(matches, token):
    devadmin = User.objects.create_superuser(username='devadmin', password='x', email='devadmin@dev.aiarena.net')

    arenaclient1 = User.objects.create_user(username='aiarenaclient-001', email='aiarenaclient-001@dev.aiarena.net',
                                            type='ARENA_CLIENT', owner=devadmin)

    arenaclient2 = User.objects.create_user(username='aiarenaclient-002', email='aiarenaclient-002@dev.aiarena.net',
                                            type='ARENA_CLIENT', owner=devadmin)

    service_user = User.objects.create_user(username='service_user', password='x', email='service_user@dev.aiarena.net',
                                            type='SERVICE')

    # if token is None it will generate a new one, otherwise it will use the one specified
    new_token = Token.objects.create(user=arenaclient1, key=token)

    season = Season.objects.create(previous_season_files_cleaned=True)
    season.open()

    devuser1 = User.objects.create_user(username='devuser1', password='x', email='devuser1@dev.aiarena.net')
    devuser2 = User.objects.create_user(username='devuser2', password='x', email='devuser2@dev.aiarena.net')

    with open(BaseTestMixin.test_map_path, 'rb') as map:
        Map.objects.create(name='test_map', file=File(map), active=True)

    with open(BaseTestMixin.test_bot_zip_path, 'rb') as bot_zip:
        Bot.objects.create(user=devadmin, name='devadmin_bot1', active=True, plays_race='T', type='python',
                           bot_zip=File(bot_zip))
        Bot.objects.create(user=devadmin, name='devadmin_bot2', active=True, plays_race='Z', type='python',
                           bot_zip=File(bot_zip))
        Bot.objects.create(user=devadmin, name='devadmin_bot3', plays_race='P', type='python',
                           bot_zip=File(bot_zip))  # inactive bot

        Bot.objects.create(user=devuser1, name='devuser1_bot1', active=True, plays_race='P', type='python',
                           bot_zip=File(bot_zip))
        Bot.objects.create(user=devuser1, name='devuser1_bot2', active=True, plays_race='Z', type='python',
                           bot_zip=File(bot_zip))
        Bot.objects.create(user=devuser1, name='devuser1_bot3', plays_race='T', type='python',
                           bot_zip=File(bot_zip))  # inactive bot

        Bot.objects.create(user=devuser2, name='devuser2_bot1', active=True, plays_race='P', type='python',
                           bot_zip=File(bot_zip))
        Bot.objects.create(user=devuser2, name='devuser2_bot2', active=True, plays_race='T', type='python',
                           bot_zip=File(bot_zip))
        Bot.objects.create(user=devuser2, name='devuser2_bot3', plays_race='Z', type='python',
                           bot_zip=File(bot_zip))  # inactive bot

    for x in range(matches - 1):
        if(bool(random.getrandbits(1))):  # select randomly
            create_result(create_match(arenaclient1), random.choice(Result.TYPES)[0], arenaclient1)
        else:
            create_result_with_bot_data_and_logs(create_match(arenaclient1), 'Player1Crash', arenaclient1)

        if x == 0:  # make it so a bot that once was active, is now inactive
            bot1 = Match.objects.get(result__isnull=False).participant1.bot
            bot1.active = False
            bot1.save()

    # so we have a match in progress
    if matches != 0:
        create_match(arenaclient1)

    return new_token


class Command(BaseCommand):
    help = "Seed database for testing and development."

    _DEFAULT_MATCHES_TO_GENERATE = 20

    def add_arguments(self, parser):
        parser.add_argument('--matches', type=int, default=self._DEFAULT_MATCHES_TO_GENERATE,
                            help="Number of matches to generate. Default is {0}.".format(
                                self._DEFAULT_MATCHES_TO_GENERATE))
        parser.add_argument('--token', type=str, default=None,
                            help="Specify the token to use for the arena client."
                                 " Useful to avoid having to reconfigure arena clients in testing")
        parser.add_argument('--flush', action='store_true', help="Whether to flush the existing database data.")
        parser.add_argument('--migrate', action='store_true', help="Whether to migrate the database first.")

    def handle(self, *args, **options):

        if settings.ENVIRONMENT_TYPE == EnvironmentType.DEVELOPMENT \
                or settings.ENVIRONMENT_TYPE == EnvironmentType.STAGING:
            if options['migrate'] is not None:
                self.stdout.write('Migrating database...')
                call_command('migrate', '--noinput')

            if options['flush'] is not None:
                self.stdout.write('Flushing data...')
                call_command('flush', '--noinput')

            self.stdout.write('Seeding data...')

            self.stdout.write('Generating {0} match(es)...'.format(options['matches']))
            api_token = run_seed(options['matches'], options['token'])

            self.stdout.write('Done. User logins have a password of "x".')
            self.stdout.write('API Token is {0}.'.format(api_token))
        else:
            self.stdout.write('Seeding failed: This is not a development or staging environment!')
