from django.core.files import File
from django.core.management.base import BaseCommand
from rest_framework.authtoken.models import Token

from aiarena import settings
from aiarena.core.models import User, Map, Bot, Match, Result
from aiarena.core.tests import BaseTestCase
from aiarena.core.utils import EnvironmentType


def create_match(as_user):
    return Match.start_next_match(as_user)


def create_result_with_bot_data_and_logs(match, type, as_user):
    with open(BaseTestCase.test_replay_path, 'rb') as result_replay,\
            open(BaseTestCase.test_bot1_data_path,'rb') as bot1_data,\
            open(BaseTestCase.test_bot2_data_path, 'rb') as bot2_data,\
            open(BaseTestCase.test_bot1_match_log_path,'rb') as bot1_log,\
            open(BaseTestCase.test_bot2_match_log_path, 'rb') as bot2_log:
        result = Result.objects.create(match=match, type=type, replay_file=File(result_replay), duration=1,
                                       submitted_by=as_user)
        result.finalize_submission(File(bot1_data), File(bot2_data), File(bot1_log), File(bot2_log))


def create_result(match, type, as_user):
    with open(BaseTestCase.test_replay_path, 'rb') as result_replay:
        result = Result.objects.create(match=match, type=type, replay_file=File(result_replay), duration=1,
                                       submitted_by=as_user)
        result.finalize_submission(None, None, None, None)


def run_seed(rounds):
    devadmin = User.objects.create_superuser(username='devadmin', password='x', email='devadmin@aiarena.net')
    Token.objects.create(user=devadmin)
    devuser = User.objects.create(username='devuser', password='x', email='devuser@aiarena.net')
    Map.objects.create(name='test_map')

    with open(BaseTestCase.test_bot_zip_path, 'rb') as bot_zip:
        Bot.objects.create(user=devadmin, name='devadmin_bot1', active=True, plays_race='T', type='python',
                           bot_zip=File(bot_zip))
        Bot.objects.create(user=devadmin, name='devadmin_bot2', active=True, plays_race='Z', type='python',
                           bot_zip=File(bot_zip))
        Bot.objects.create(user=devadmin, name='devadmin_bot3', plays_race='P', type='python',
                           bot_zip=File(bot_zip))  # inactive bot

        Bot.objects.create(user=devuser, name='devuser_bot1', active=True, plays_race='P', type='python',
                           bot_zip=File(bot_zip))
        Bot.objects.create(user=devuser, name='devuser_bot2', active=True, plays_race='Z', type='python',
                           bot_zip=File(bot_zip))
        Bot.objects.create(user=devuser, name='devuser_bot3', plays_race='T', type='python',
                           bot_zip=File(bot_zip))  # inactive bot

    for x in range(rounds-1):  # 4 active bots - 6 games per round
        match = create_match(devadmin)
        create_result(match, 'Player1Win', devadmin)
        match = create_match(devadmin)
        create_result(match, 'Player2Win', devadmin)
        match = create_match(devadmin)
        create_result_with_bot_data_and_logs(match, 'Player1Crash', devadmin)
        match = create_match(devadmin)
        create_result(match, 'Player1TimeOut', devadmin)
        match = create_match(devadmin)
        create_result_with_bot_data_and_logs(match, 'Tie', devadmin)
        match = create_match(devadmin)
        create_result(match, 'Timeout', devadmin)

    # one last to tick over into the final round so we don't have an empty match queue
    create_match(devadmin)


class Command(BaseCommand):
    help = "Seed database for testing and development."

    _DEFAULT_ROUNDS_TO_GENERATE = 10

    def add_arguments(self, parser):
        parser.add_argument('--rounds', type=int, help="Number of rounds to generate")

    def handle(self, *args, **options):
        self.stdout.write('Seeding data...')

        if settings.ENVIRONMENT_TYPE == EnvironmentType.DEVELOPMENT:
            if options['rounds'] is not None:
                rounds = options['rounds']
            else:
                rounds = self._DEFAULT_ROUNDS_TO_GENERATE

            self.stdout.write('Generating {0} round(s)...'.format(rounds))
            run_seed(rounds)
        else:
            self.stdout.write('Seeding failed: This is not a development environment!')

        self.stdout.write('Done.')
