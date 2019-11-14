import os
from datetime import timedelta
from io import StringIO

from constance import config
from django.core.exceptions import ValidationError
from django.core.files import File
from django.core.files.uploadedfile import SimpleUploadedFile
from django.core.management import call_command, CommandError
from django.test import TransactionTestCase
from django.utils import timezone

from aiarena import settings
from aiarena.core.management.commands import cleanupreplays
from aiarena.core.models import User, Bot, Map, Match, Result, MatchParticipation, Season, SeasonParticipation, Round
from aiarena.core.utils import calculate_md5


class BaseTestCase(TransactionTestCase):
    # For some reason using an absolute file path here will cause it to mangle the save directory and fail
    # later whilst handling the bot_zip file save
    test_bot_zip_path = 'aiarena/core/test-media/test_bot.zip'
    test_bot_zip_hash = 'c96bcfc79318a8b50b0b2c8696400d06'
    test_bot_zip_updated_path = 'aiarena/core/test-media/test_bot_updated.zip'
    test_bot_zip_updated_hash = '685dba7a89511157a6594c20c50397d3'
    test_bot1_data_path = 'aiarena/core/test-media/test_bot1_data.zip'
    test_bot1_data_hash = '855994f4cb90e1220b3b2819a0ed1cc7'
    test_bot2_data_path = 'aiarena/core/test-media/test_bot2_data.zip'
    test_bot2_data_hash = '0579988bdab3a23cdf54998ae1d531db'
    test_bot1_match_log_path = 'aiarena/core/test-media/test_bot1_match_log.zip'
    test_bot2_match_log_path = 'aiarena/core/test-media/test_bot2_match_log.zip'
    test_arenaclient_log_path = 'aiarena/core/test-media/test_arenaclient_log.zip'
    test_replay_path = 'aiarena/core/test-media/testReplay.SC2Replay'
    test_map_path = 'aiarena/core/test-media/AutomatonLE.SC2Map'

    def _create_map(self, name):
        return Map.objects.create(name=name, active=True)

    def _create_open_season(self):
        season = Season.objects.create()
        season.open()
        return season

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
        filename = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'test-media/testReplay.SC2Replay')
        with open(filename, 'rb') as replayFile, open(self.test_bot1_data_path, 'rb') as bot1_data, open(
                self.test_bot2_data_path, 'rb') as bot2_data, open(self.test_bot1_match_log_path,
                                                                   'rb') as bot1_log, open(
            self.test_bot2_match_log_path, 'rb') as bot2_log, open(self.test_arenaclient_log_path,
                                                                   'rb') as arenaclient_log:
            return self.client.post('/api/arenaclient/results/',
                                    {'match': match_id,
                                     'type': result_type,
                                     'replay_file': SimpleUploadedFile("replayFile.SC2Replay", replayFile.read()),
                                     'game_steps': 500,
                                     'bot1_data': SimpleUploadedFile("bot1_data.zip", bot1_data.read()),
                                     'bot2_data': SimpleUploadedFile("bot2_data.zip", bot2_data.read()),
                                     'bot1_log': SimpleUploadedFile("bot1_log.zip", bot1_log.read()),
                                     'bot2_log': SimpleUploadedFile("bot2_log.zip", bot2_log.read()),
                                     'bot1_avg_step_time': 0.2,
                                     'bot2_avg_step_time': 0.1,
                                     'arenaclient_log': SimpleUploadedFile("arenaclient_log.zip",
                                                                           arenaclient_log.read())})

    # todo:
    def _post_to_results_no_bot_datas(self, match_id, result_type):
        filename = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'test-media/testReplay.SC2Replay')
        with open(filename, 'rb') as replayFile:
            return self.client.post('/api/arenaclient/results/',
                                    {'match': match_id,
                                     'type': result_type,
                                     'replay_file': SimpleUploadedFile("replayFile.SC2Replay", replayFile.read()),
                                     'game_steps': 500})

    def _post_to_results_no_bot1_data(self, match_id, result_type):
        filename = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'test-media/testReplay.SC2Replay')
        with open(filename, 'rb') as replayFile, open(self.test_bot2_data_path, 'rb') as bot2_data:
            return self.client.post('/api/arenaclient/results/',
                                    {'match': match_id,
                                     'type': result_type,
                                     'replay_file': SimpleUploadedFile("replayFile.SC2Replay", replayFile.read()),
                                     'game_steps': 500,
                                     'bot2_data': SimpleUploadedFile("bot2_data.zip", bot2_data.read())})

    def _post_to_results_no_bot2_data(self, match_id, result_type):
        filename = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'test-media/testReplay.SC2Replay')
        with open(filename, 'rb') as replayFile, open(self.test_bot1_data_path, 'rb') as bot1_data:
            return self.client.post('/api/arenaclient/results/',
                                    {'match': match_id,
                                     'type': result_type,
                                     'replay_file': SimpleUploadedFile("replayFile.SC2Replay", replayFile.read()),
                                     'game_steps': 500,
                                     'bot1_data': SimpleUploadedFile("bot1_data.zip", bot1_data.read())})

    def _post_to_results_no_replay(self, match_id, result_type):
        return self.client.post('/api/arenaclient/results/',
                                {'match': match_id,
                                 'type': result_type,
                                 'replay_file': '',
                                 'game_steps': 500})

    def _generate_full_data_set(self):
        self.client.login(username='staff_user', password='x')

        self._create_map('testmap2')
        self._generate_extra_users()
        self._generate_extra_bots()

        self._generate_match_activity()

        # generate a bot match request to ensure it doesn't bug things out
        bot = Bot.get_random_available()
        call_command('requestbotmatch', bot.id)

        self.client.logout()  # child tests can login if they require

    def _generate_match_activity(self):
        response = self._post_to_matches()
        self.assertEqual(response.status_code, 201)
        response = self._post_to_results_no_replay(response.data['id'], 'InitializationError')
        self.assertEqual(response.status_code, 201)

        response = self._post_to_matches()
        self.assertEqual(response.status_code, 201)
        response = self._post_to_results(response.data['id'], 'MatchCancelled')
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
                                                     email='regular_user2@dev.aiarena.net')
        self.regularUser3 = User.objects.create_user(username='regular_user3', password='x',
                                                     email='regular_user3@dev.aiarena.net')
        self.regularUser4 = User.objects.create_user(username='regular_user4', password='x',
                                                     email='regular_user4@dev.aiarena.net')


class LoggedInTestCase(BaseTestCase):
    def setUp(self):
        super(LoggedInTestCase, self).setUp()

        self.staffUser1 = User.objects.create_user(username='staff_user', password='x', email='staff_user@dev.aiarena.net',
                                                   is_staff=True)

        self.arenaclientUser1 = User.objects.create_user(username='arenaclient1', email='arenaclient@dev.aiarena.net',
                                                         type='ARENA_CLIENT')
        self.regularUser1 = User.objects.create_user(username='regular_user1', password='x',
                                                     email='regular_user1@dev.aiarena.net')


class MatchReadyTestCase(LoggedInTestCase):
    def setUp(self):
        super(MatchReadyTestCase, self).setUp()

        # raise the configured per user limits
        config.MAX_USER_BOT_COUNT_ACTIVE_PER_RACE = 10
        config.MAX_USER_BOT_COUNT = 10

        self._create_open_season()
        self._create_map('testmap1')

        self.regularUser1Bot1 = self._create_active_bot(self.regularUser1, 'regularUser1Bot1', 'T')
        self.regularUser1Bot2 = self._create_active_bot(self.regularUser1, 'regularUser1Bot2', 'Z')
        self.regularUser1Bot2 = self._create_bot(self.regularUser1, 'regularUser1Bot3', 'P')  # inactive bot for realism
        self.staffUser1Bot1 = self._create_active_bot(self.staffUser1, 'staffUser1Bot1', 'T')
        self.staffUser1Bot2 = self._create_active_bot(self.staffUser1, 'staffUser1Bot2', 'Z')


# Use this to pre-build a fuller dataset for testing
class FullDataSetTestCase(MatchReadyTestCase):
    def setUp(self):
        super(FullDataSetTestCase, self).setUp()
        self._generate_full_data_set()


class UtilsTestCase(BaseTestCase):
    def test_calc_md5(self):
        filename = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'test-media/test_bot.zip')
        self.assertEqual('c96bcfc79318a8b50b0b2c8696400d06', calculate_md5(filename))


class UserTestCase(BaseTestCase):
    def test_user_creation(self):
        user = User.objects.create(username='test user', email='test@test.com')
        arenaclient = User.objects.create(username='test arenaclient', email='arenaclient@test.com')
        arenaclient.type = 'ARENA_CLIENT'
        with self.assertRaises(ValidationError):
            arenaclient.clean()
        arenaclient.owner = user
        arenaclient.clean()


class BotTestCase(LoggedInTestCase):
    def test_bot_creation_and_update(self):
        # set the configured per user limits for this test
        config.MAX_USER_BOT_COUNT_ACTIVE_PER_RACE = 1
        config.MAX_USER_BOT_COUNT = 4

        # required for active bot
        self._create_open_season()

        # create bot along with bot data
        with open(self.test_bot_zip_path, 'rb') as bot_zip, open(self.test_bot1_data_path, 'rb') as bot_data:
            bot1 = Bot(user=self.regularUser1, name='testbot', bot_zip=File(bot_zip), bot_data=File(bot_data),
                       plays_race='T', type='python', active=True)
            bot1.full_clean()
            bot1.save()

        # test display id regen
        prev_bot_display_id = bot1.game_display_id
        bot1.regen_game_display_id()
        self.assertNotEqual(bot1.game_display_id, prev_bot_display_id)

        bot1.refresh_from_db()
        # check hashes
        self.assertEqual(self.test_bot_zip_hash, bot1.bot_zip_md5hash)
        self.assertEqual(self.test_bot1_data_hash, bot1.bot_data_md5hash)

        # check the bot file now exists
        self.assertTrue(os.path.isfile('./private-media/bots/{0}/bot_zip'.format(bot1.id)))

        with open(self.test_bot_zip_path, 'rb') as bot_zip:
            bot1.bot_zip = File(bot_zip)
            bot1.save()

        # check the bot file backup now exists
        self.assertTrue(os.path.isfile('./private-media/bots/{0}/bot_zip_backup'.format(bot1.id)))

        # test max bots for user
        for i in range(1, config.MAX_USER_BOT_COUNT):
            self._create_bot(self.regularUser1, 'testbot{0}'.format(i))
        with self.assertRaisesMessage(ValidationError,
                                      'Maximum bot count of {0} already reached. '
                                      'No more bots may be added for this user.'.format(config.MAX_USER_BOT_COUNT)):
            self._create_bot(self.regularUser1, 'testbot{0}'.format(config.MAX_USER_BOT_COUNT))

        # test active bots per race limit for user
        # all bots should be the same race, so just pick any
        inactive_bot = Bot.objects.filter(user=self.regularUser1, active=False)[0]
        with self.assertRaisesMessage(ValidationError,
                                      'Too many active bots playing that race already exist for this user.'
                                      'You are allowed 1 active bot(s) per race.'):
            inactive_bot.active = True
            inactive_bot.full_clean()  # run validation

        # test updating bot_zip
        with open(self.test_bot_zip_updated_path, 'rb') as bot_zip_updated:
            bot1.bot_zip = File(bot_zip_updated)
            bot1.save()

        bot1.refresh_from_db()
        self.assertEqual(self.test_bot_zip_updated_hash, bot1.bot_zip_md5hash)

        # test updating bot_data
        # using bot2's data instead here so it's different
        with open(self.test_bot2_data_path, 'rb') as bot_data_updated:
            bot1.bot_data = File(bot_data_updated)
            bot1.save()

        bot1.refresh_from_db()
        self.assertEqual(self.test_bot2_data_hash, bot1.bot_data_md5hash)


class SeasonsTestCase(FullDataSetTestCase):
    """
    Test season rotation
    """

    def _finish_season_rounds(self):
        for x in range(Match.objects.filter(result__isnull=True).count()):
            response = self._post_to_matches()
            self.assertEqual(response.status_code, 201)

            response = self._post_to_results(response.data['id'], 'Player1Win')
            self.assertEqual(response.status_code, 201)

    def test_season_states(self):
        self.client.login(username='arenaclient1', password='x')

        self.assertEqual(Match.objects.filter(result__isnull=True).count(), 12,
                         msg='This tests expects 12 unplayed matches in order to work.')

        # attempt to close season - should fail
        season1 = Season.objects.get()
        self.assertEqual(season1.number, 1)

        season1.pause()

        self._finish_season_rounds()

        response = self._post_to_matches()
        self.assertEqual(response.status_code, 503)
        self.assertEqual(u'The current season is paused.', response.data['detail'])

        # reopen the season
        season1.open()

        # start a new round
        response = self._post_to_matches()
        self.assertEqual(response.status_code, 201)

        season1.start_closing()

        # finish the season
        self._finish_season_rounds()

        # successful close
        season1.refresh_from_db()
        self.assertEqual(season1.status, 'closed')

        # check that bots are all deactivated
        for bot in Bot.objects.all():
            self.assertFalse(bot.active)

        # Activating a bot should fail
        with self.assertRaises(ValidationError):
            bot = Bot.objects.all()[0]
            bot.active = True
            bot.full_clean()


        # start a new season
        season2 = Season.objects.create()
        self.assertEqual(season2.number, 2)

        # not enough active bots
        response = self._post_to_matches()
        self.assertEqual(response.status_code, 409)
        self.assertEqual(u'Not enough available bots for a match. Wait until more bots become available.', response.data['detail'])

        # activate the bots
        for bot in Bot.objects.all():
            bot.active = True
            bot.save()

        # current season is paused
        response = self._post_to_matches()
        self.assertEqual(response.status_code, 503)
        self.assertEqual(u'The current season is paused.', response.data['detail'])

        season2.open()

        # start a new round
        response = self._post_to_matches()
        self.assertEqual(response.status_code, 201)

        # New round should be number 1 for the new season
        round = Round.objects.get(season=season2)
        self.assertEqual(round.number, 1)

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

    def test_cleanup_replays_and_logs(self):
        NUM_MATCHES = 12
        self.client.login(username='staff_user', password='x')
        # generate some matches so we have replays to delete...
        for x in range(NUM_MATCHES):  # 12 = two rounds
            response = self._post_to_matches()
            self.assertEqual(response.status_code, 201)
            match_id = response.data['id']
            self._post_to_results(match_id, 'Player1Win')

        # double check the replay and log files exist
        results = Result.objects.filter(replay_file__isnull=False)
        self.assertEqual(results.count(), NUM_MATCHES)
        # after we ensure the arena client log count matches, we can safely just use the above results list
        results_logs = Result.objects.filter(arenaclient_log__isnull=False)
        self.assertEqual(results_logs.count(), NUM_MATCHES)
        participants = MatchParticipation.objects.filter(match_log__isnull=False)
        self.assertEqual(participants.count(), NUM_MATCHES * 2)

        # set the created time so they'll be purged
        results.update(created=timezone.now() - timedelta(days=cleanupreplays.Command._DEFAULT_DAYS_LOOKBACK + 1))

        out = StringIO()
        call_command('cleanupreplays', stdout=out)
        self.assertIn(
            'Cleaning up replays starting from 30 days into the past...\nCleaned up {0} replays.'.format(NUM_MATCHES),
            out.getvalue())

        self.assertEqual(results.count(), NUM_MATCHES)
        for result in results:
            self.assertFalse(result.replay_file)

        call_command('cleanuparenaclientlogfiles', stdout=out)
        self.assertIn(
            'Cleaning up arena client logfiles starting from 30 days into the past...\nCleaned up {0} logfiles.'.format(
                NUM_MATCHES),
            out.getvalue())

        self.assertEqual(results.count(), NUM_MATCHES)
        for result in results:
            self.assertFalse(result.replay_file)

        call_command('cleanupmatchlogfiles', stdout=out)
        self.assertIn(
            'Cleaning up match logfiles starting from 30 days into the past...\nCleaned up {0} logfiles.'.format(
                NUM_MATCHES * 2),
            out.getvalue())

        self.assertEqual(participants.count(), NUM_MATCHES * 2)
        for participant in participants:
            self.assertFalse(participant.match_log)

    def test_generatestats(self):
        self._generate_full_data_set()
        out = StringIO()
        call_command('generatestats', stdout=out)
        self.assertIn('Generating stats...\nDone', out.getvalue())

    def test_request_bot_match_random_opponent(self):
        out = StringIO()
        call_command('requestbotmatch', '1', stdout=out)
        self.assertIn('Successfully requested match. Match ID:', out.getvalue())

    def test_seed(self):
        out = StringIO()
        call_command('seed', stdout=out)
        self.assertIn('Done. User logins have a password of "x".', out.getvalue())
