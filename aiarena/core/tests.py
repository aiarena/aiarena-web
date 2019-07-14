import os
from io import StringIO

from django.core.exceptions import ValidationError
from django.core.files import File
from django.core.management import call_command, CommandError
from django.test import TransactionTestCase

from aiarena import settings
from aiarena.core.models import User, Bot, Map, Match
from aiarena.core.utils import calculate_md5
from aiarena.settings import MAX_USER_BOT_COUNT


class BaseTestCase(TransactionTestCase):
    # For some reason using an absolute file path here will cause it to mangle the save directory and fail
    # later whilst handling the bot_zip file save
    test_bot_zip_path = 'aiarena/core/test_bot.zip'
    test_bot1_data_path = 'aiarena/core/test_bot1_data.zip'
    test_bot2_data_path = 'aiarena/core/test_bot2_data.zip'
    test_bot1_match_log_path = 'aiarena/core/test_bot1_match_log.zip'
    test_bot2_match_log_path = 'aiarena/core/test_bot2_match_log.zip'
    test_replay_path = 'aiarena/core/testReplay.SC2Replay'

    def _create_map(self, name):
        return Map.objects.create(name=name)

    def _create_bot(self, user, name, plays_race='T'):
        with open(self.test_bot_zip_path, 'rb') as bot_zip, open(self.test_bot1_data_path, 'rb') as bot_data:
            bot = Bot(user=user, name=name, bot_zip=File(bot_zip), bot_data=File(bot_data), plays_race=plays_race,
                      type='python')
            bot.full_clean()
            bot.save()
            return bot

    def _create_active_bot(self, user, name, plays_race='T'):
        with open(self.test_bot_zip_path, 'rb') as bot_zip:
            bot = Bot(user=user, name=name, bot_zip=File(bot_zip), plays_race=plays_race, type='python', active=True)
            bot.full_clean()
            bot.save()
            return bot

    def _post_to_matches(self):
        return self.client.post('/api/arenaclient/matches/')

    def _post_to_results(self, match_id, result_type):
        filename = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'testReplay.SC2Replay')
        with open(filename) as replayFile, open(self.test_bot1_data_path) as bot1_data, open(
                self.test_bot2_data_path) as bot2_data, open(self.test_bot1_match_log_path) as bot1_log, open(
                self.test_bot2_match_log_path) as bot2_log:
            return self.client.post('/api/arenaclient/results/',
                                    {'match': match_id,
                                     'type': result_type,
                                     'replay_file': replayFile,
                                     'duration': 500,
                                     'bot1_data': bot1_data,
                                     'bot2_data': bot2_data,
                                     'bot1_log': bot1_log,
                                     'bot2_log': bot2_log})

    def _post_to_results_no_bot_datas(self, match_id, result_type):
        filename = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'testReplay.SC2Replay')
        with open(filename) as replayFile:
            return self.client.post('/api/arenaclient/results/',
                                    {'match': match_id,
                                     'type': result_type,
                                     'replay_file': replayFile,
                                     'duration': 500})

    def _post_to_results_no_bot1_data(self, match_id, result_type):
        filename = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'testReplay.SC2Replay')
        with open(filename) as replayFile, open(self.test_bot1_data_path) as bot2_data:
            return self.client.post('/api/arenaclient/results/',
                                    {'match': match_id,
                                     'type': result_type,
                                     'replay_file': replayFile,
                                     'duration': 500,
                                     'bot2_data': bot2_data})

    def _post_to_results_no_bot2_data(self, match_id, result_type):
        filename = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'testReplay.SC2Replay')
        with open(filename) as replayFile, open(self.test_bot1_data_path) as bot1_data:
            return self.client.post('/api/arenaclient/results/',
                                    {'match': match_id,
                                     'type': result_type,
                                     'replay_file': replayFile,
                                     'duration': 500,
                                     'bot1_data': bot1_data})

    def _post_to_results_no_replay(self, match_id, result_type):
        return self.client.post('/api/arenaclient/results/',
                                {'match': match_id,
                                 'type': result_type,
                                 'replay_file': '',
                                 'duration': 500})


class LoggedInTestCase(BaseTestCase):
    def setUp(self):
        super(LoggedInTestCase, self).setUp()

        self.staffUser1 = User.objects.create_user(username='staff_user', password='x', email='staff_user@aiarena.net',
                                                   is_staff=True)
        self.regularUser1 = User.objects.create_user(username='regular_user1', password='x',
                                                     email='regular_user1@aiarena.net')


class MatchReadyTestCase(LoggedInTestCase):
    def setUp(self):
        super(MatchReadyTestCase, self).setUp()

        self.regularUser1Bot1 = self._create_active_bot(self.regularUser1, 'regularUser1Bot1', 'T')
        self.regularUser1Bot2 = self._create_active_bot(self.regularUser1, 'regularUser1Bot2', 'Z')
        self.regularUser1Bot2 = self._create_bot(self.regularUser1, 'regularUser1Bot3', 'P')  # inactive bot for realism
        self.staffUser1Bot1 = self._create_active_bot(self.staffUser1, 'staffUser1Bot1', 'T')
        self.staffUser1Bot2 = self._create_active_bot(self.staffUser1, 'staffUser1Bot2', 'Z')
        self._create_map('testmap1')


# Use this to pre-build a fuller dataset for testing
class FullDataSetTestCase(MatchReadyTestCase):

    def setUp(self):
        super(FullDataSetTestCase, self).setUp()
        self.client.login(username='staff_user', password='x')

        self._create_map('testmap2')
        self._generate_extra_users()
        self._generate_extra_bots()

        self._generate_match_activity()
        self.client.logout()  # child tests can login if they require

    def _generate_match_activity(self):
        response = self._post_to_matches()
        self.assertEqual(response.status_code, 201)
        response = self._post_to_results_no_replay(response.data['id'], 'InitializationError')
        self.assertEqual(response.status_code, 201)

        response = self._post_to_matches()
        self.assertEqual(response.status_code, 201)
        response = self._post_to_results(response.data['id'], 'Timeout')
        self.assertEqual(response.status_code, 201)

        response = self._post_to_matches()
        self.assertEqual(response.status_code, 201)
        response = self._post_to_results_no_bot1_data(response.data['id'], 'Player1Win')
        self.assertEqual(response.status_code, 201)

        response = self._post_to_matches()
        self.assertEqual(response.status_code, 201)
        response = self._post_to_results_no_bot2_data(response.data['id'], 'Player1Crash')
        self.assertEqual(response.status_code, 201)

        response = self._post_to_matches()
        self.assertEqual(response.status_code, 201)
        response = self._post_to_results(response.data['id'], 'Player1TimeOut')
        self.assertEqual(response.status_code, 201)

        response = self._post_to_matches()
        self.assertEqual(response.status_code, 201)
        response = self._post_to_results_no_bot_datas(response.data['id'], 'Player2Win')
        self.assertEqual(response.status_code, 201)

        response = self._post_to_matches()
        self.assertEqual(response.status_code, 201)
        response = self._post_to_results_no_bot_datas(response.data['id'], 'Player2Crash')
        self.assertEqual(response.status_code, 201)

        response = self._post_to_matches()
        self.assertEqual(response.status_code, 201)
        response = self._post_to_results(response.data['id'], 'Player2TimeOut')
        self.assertEqual(response.status_code, 201)

        response = self._post_to_matches()
        self.assertEqual(response.status_code, 201)
        response = self._post_to_results(response.data['id'], 'Tie')
        self.assertEqual(response.status_code, 201)

        response = self._post_to_matches()
        self.assertEqual(response.status_code, 201)
        response = self._post_to_results_no_replay(response.data['id'], 'Error')
        self.assertEqual(response.status_code, 201)

    def _generate_extra_bots(self):
        self.regularUser2Bot1 = self._create_bot(self.regularUser2, 'regularUser2Bot1')
        self.regularUser2Bot2 = self._create_active_bot(self.regularUser2, 'regularUser2Bot2')
        self.regularUser3Bot1 = self._create_active_bot(self.regularUser3, 'regularUser3Bot1')
        self.regularUser3Bot2 = self._create_active_bot(self.regularUser3, 'regularUser3Bot2', 'Z')
        self.regularUser4Bot1 = self._create_bot(self.regularUser4, 'regularUser4Bot1')
        self.regularUser4Bot2 = self._create_bot(self.regularUser4, 'regularUser4Bot2')

    def _generate_extra_users(self):
        self.regularUser2 = User.objects.create_user(username='regular_user2', password='x',
                                                     email='regular_user2@aiarena.net')
        self.regularUser3 = User.objects.create_user(username='regular_user3', password='x',
                                                     email='regular_user3@aiarena.net')
        self.regularUser4 = User.objects.create_user(username='regular_user4', password='x',
                                                     email='regular_user4@aiarena.net')


class UtilsTestCase(BaseTestCase):
    def test_calc_md5(self):
        filename = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'test_bot.zip')
        self.assertEqual('7411028ba931baaad47bf5810215e4f8', calculate_md5(filename))


class UserTestCase(BaseTestCase):
    def test_user_creation(self):
        User.objects.create(username='test user', email='test@test.com')


class BotTestCase(LoggedInTestCase):
    def test_bot_creation(self):
        # create bot along with bot data
        with open(self.test_bot_zip_path, 'rb') as bot_zip, open(self.test_bot1_data_path, 'rb') as bot_data:
            bot1 = Bot(user=self.regularUser1, name='testbot', bot_zip=File(bot_zip), bot_data=File(bot_data),
                       plays_race='T', type='python', active=True)
            bot1.full_clean()
            bot1.save()

        # check hashes
        self.assertEqual('7411028ba931baaad47bf5810215e4f8', bot1.bot_zip_md5hash)
        self.assertEqual('6cc8ec3fa50d069eab74835757807ef2', bot1.bot_data_md5hash)

        # check the bot file now exists
        self.assertTrue(os.path.isfile('./private-media/bots/{0}/bot_zip'.format(bot1.id)))

        with open(self.test_bot_zip_path, 'rb') as bot_zip:
            bot1.bot_zip = File(bot_zip)
            bot1.save()

        # check the bot file backup now exists
        self.assertTrue(os.path.isfile('./private-media/bots/{0}/bot_zip_backup'.format(bot1.id)))

        # test max bots for user
        for i in range(1, MAX_USER_BOT_COUNT):
            self._create_bot(self.regularUser1, 'testbot{0}'.format(i))
        with self.assertRaisesMessage(ValidationError,
                                      'Maximum bot count of {0} already reached. '
                                      'No more bots may be added for this user.'.format(MAX_USER_BOT_COUNT)):
            self._create_bot(self.regularUser1, 'testbot{0}'.format(MAX_USER_BOT_COUNT))

        # test active bots per race limit for user
        # all bots should be the same race, so just pick any
        inactive_bot = Bot.objects.filter(user=self.regularUser1, active=False)[0]
        with self.assertRaisesMessage(ValidationError,
                                      'Too many active bots playing that race already exist for this user.'
                                      ' Each user can only have 1 active bot(s) per race.'):
            inactive_bot.active = True
            inactive_bot.full_clean()  # run validation


class PageRenderTestCase(FullDataSetTestCase):
    """
    Tests to ensure website pages don't break.
    """

    def test_get_index_page(self):
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)

    def test_get_bots_page(self):
        response = self.client.get('/bots/')
        self.assertEqual(response.status_code, 200)

    def test_get_bot_page(self):
        response = self.client.get('/bots/{0}/'.format(self.regularUser1Bot1.id))
        self.assertEqual(response.status_code, 200)

    def test_get_bot_edit_page(self):
        self.client.login(username='regular_user1', password='x')
        # test bot edit pages we can access
        bots = Bot.objects.filter(user=self.regularUser1)
        for bot in bots:
            response = self.client.get('/bots/{0}/edit'.format(bot.pk))
            self.assertEqual(response.status_code, 200)

        # test bot edit pages we can't access
        bots = Bot.objects.exclude(user=self.regularUser1)
        for bot in bots:
            response = self.client.get('/bots/{0}/edit'.format(bot.pk))
            self.assertEqual(response.status_code, 404)

    def test_get_author_page(self):
        response = self.client.get('/authors/')
        self.assertEqual(response.status_code, 200)

    def test_get_authors_page(self):
        response = self.client.get('/authors/{0}/'.format(self.regularUser1.id))
        self.assertEqual(response.status_code, 200)

    def test_get_ranking_page(self):
        response = self.client.get('/ranking/')
        self.assertEqual(response.status_code, 200)

    def test_get_results_page(self):
        response = self.client.get('/results/')
        self.assertEqual(response.status_code, 200)

    def test_get_rules_page(self):
        response = self.client.get('/rules/')
        self.assertEqual(response.status_code, 200)

    def test_get_login_page(self):
        response = self.client.get('/accounts/login/')
        self.assertEqual(response.status_code, 200)

    def test_get_register_page(self):
        response = self.client.get('/accounts/register/')
        self.assertEqual(response.status_code, 200)

    def test_get_reset_password_page(self):
        response = self.client.get('/accounts/password_reset/')
        self.assertEqual(response.status_code, 200)

    def test_get_stream_page(self):
        response = self.client.get('/stream/')
        self.assertEqual(response.status_code, 200)

    def test_get_match_queue_page(self):
        response = self.client.get('/match-queue/')
        self.assertEqual(response.status_code, 200)


class PrivateStorageTestCase(MatchReadyTestCase):
    pass  # todo


class ManagementCommandTests(MatchReadyTestCase):
    """
    Tests for management commands
    """

    def test_cancel_matches(self):
        botCount = Bot.objects.filter(active=True).count()
        expectedMatchCountPerRound = int(botCount / 2 * (botCount - 1))

        # test match doesn't exist
        with self.assertRaisesMessage(CommandError, 'Match "12345" does not exist'):
            call_command('cancelmatches', '12345')

        # test match successfully cancelled
        self.client.login(username='staff_user', password='x')
        response = self._post_to_matches()
        self.assertEqual(response.status_code, 201)
        match_id = response.data['id']

        out = StringIO()
        call_command('cancelmatches', match_id, stdout=out)
        self.assertIn('Successfully marked match "{0}" with MatchCancelled'.format(match_id), out.getvalue())

        # test result already exists
        with self.assertRaisesMessage(CommandError, 'A result already exists for match "{0}"'.format(match_id)):
            call_command('cancelmatches', match_id)

        # test that cancelling the match marks it as started.
        self.assertIsNotNone(Match.objects.get(id=match_id).started)

        # cancel the rest of the matches.
        for x in range(1, expectedMatchCountPerRound):
            response = self._post_to_matches()
            self.assertEqual(response.status_code, 201)
            match_id = response.data['id']

            out = StringIO()
            call_command('cancelmatches', match_id, stdout=out)
            self.assertIn('Successfully marked match "{0}" with MatchCancelled'.format(match_id),
                          out.getvalue())

            # test result already exists
            with self.assertRaisesMessage(CommandError, 'A result already exists for match "{0}"'.format(match_id)):
                call_command('cancelmatches', match_id)

            # test that cancelling the match marks it as started.
            self.assertIsNotNone(Match.objects.get(id=match_id).started)

        # check that the round was correctly marked as finished
        round = Match.objects.get(id=match_id).round
        self.assertTrue(round.complete)
        self.assertIsNotNone(round.finished)

    def test_reset_elo(self):
        # test match successfully cancelled
        self.client.login(username='staff_user', password='x')
        response = self._post_to_matches()
        self.assertEqual(response.status_code, 201)
        response = self._post_to_results(response.data['id'], 'Player1Win')
        self.assertEqual(response.status_code, 201)

        out = StringIO()
        call_command('resetelo', stdout=out)
        self.assertIn('ELO values have been reset.', out.getvalue())

        for bot in Bot.objects.all():
            self.assertEqual(bot.elo, settings.ELO_START_VALUE)

    def test_seed(self):
        # test match successfully cancelled
        out = StringIO()
        call_command('seed', stdout=out)
        self.assertIn('Done. User logins have a password of "x".', out.getvalue())
