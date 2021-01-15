import os
from datetime import timedelta
from io import StringIO

from constance import config
from django.core.exceptions import ValidationError
from django.core.files import File
from django.core.files.uploadedfile import SimpleUploadedFile
from django.core.management import call_command, CommandError
from django.test import TestCase, TransactionTestCase
from django.utils import timezone
from rest_framework.authtoken.models import Token

from aiarena.core.api import Matches
from aiarena.core.management.commands import cleanupreplays
from aiarena.core.models import User, Bot, Map, Match, Result, MatchParticipation, Competition, Round, ArenaClient, \
    CompetitionParticipation
from aiarena.core.models.game_type import GameMode
from aiarena.core.utils import calculate_md5

from django_fakeredis import FakeRedis


class BaseTestMixin(object):
    """
    Base test case for testing. Contains references to all the test files such as test bot zips etc.
    """
    # For some reason using an absolute file path here will cause it to mangle the save directory and fail
    # later whilst handling the bot_zip file save
    test_bot_zip_path = 'aiarena/core/tests/test-media/test_bot.zip'
    test_bot_zip_hash = 'c96bcfc79318a8b50b0b2c8696400d06'
    test_bot_zip_updated_path = 'aiarena/core/tests/test-media/test_bot_updated.zip'
    test_bot_zip_updated_hash = '685dba7a89511157a6594c20c50397d3'
    test_bot_datas = {
        'bot1': [
            {
                'path': 'aiarena/core/tests/test-media/test_bot1_data0.zip',
                'hash': '8a2ed68ea1d98f699d7f03bd98c6530d'
            },
            {
                'path': 'aiarena/core/tests/test-media/test_bot1_data1.zip',
                'hash': 'c174816d0730c76cc649cf35b097d61e'
            }
        ],
        'bot2': [
            {
                'path': 'aiarena/core/tests/test-media/test_bot2_data0.zip',
                'hash': 'de998ff5944d17eb40e37429b162b651'
            },
            {
                'path': 'aiarena/core/tests/test-media/test_bot2_data1.zip',
                'hash': '2d7ecb911b1da870a503acf4173be642'
            }
        ]
    }
    test_bot1_match_log_path = 'aiarena/core/tests/test-media/test_bot1_match_log.zip'
    test_bot2_match_log_path = 'aiarena/core/tests/test-media/test_bot2_match_log.zip'
    test_arenaclient_log_path = 'aiarena/core/tests/test-media/test_arenaclient_log.zip'
    test_replay_path = 'aiarena/core/tests/test-media/testReplay.SC2Replay'
    test_map_path = 'aiarena/core/tests/test-media/AutomatonLE.SC2Map'

    @FakeRedis("django_redis.get_redis_connection")
    def setUp(self):
        from aiarena.core.tests.testing_utils import TestingClient  # avoid circular import
        self.test_client = TestingClient(self.client)

    @FakeRedis("django_redis.get_redis_connection")
    def _create_map_for_competition(self, name, competition_id):
        competition = Competition.objects.get(id=competition_id)
        map = Map.objects.create(name=name, game_mode=competition.game_mode)
        map.competitions.add(competition)
        return map

    @FakeRedis("django_redis.get_redis_connection")
    def _create_open_competition(self, gamemode_id: int):
        competition = Competition.objects.create(name='Competition 1', type='L', game_mode_id=gamemode_id)
        competition.open()
        return competition

    @FakeRedis("django_redis.get_redis_connection")
    def _create_game_mode_and_open_competition(self):
        game = self.test_client.create_game("StarCraft II")
        gamde_mode = self.test_client.create_gamemode('Melee', game.id)
        competition = self.test_client.create_competition('Competition 1', 'L', gamde_mode.id)
        self.test_client.open_competition(competition.id)
        return competition

    @FakeRedis("django_redis.get_redis_connection")
    def _create_bot(self, user, name, plays_race='T'):
        with open(self.test_bot_zip_path, 'rb') as bot_zip, open(self.test_bot_datas['bot1'][0]['path'], 'rb') as bot_data:
            bot = Bot(user=user, name=name, bot_zip=File(bot_zip), bot_data=File(bot_data), plays_race=plays_race,
                      type='python')
            bot.full_clean()
            bot.save()
            return bot

    @FakeRedis("django_redis.get_redis_connection")
    def _create_active_bot_for_competition(self, competition_id: int, user, name, plays_race='T'):
        with open(self.test_bot_zip_path, 'rb') as bot_zip:
            bot = Bot(user=user, name=name, bot_zip=File(bot_zip), plays_race=plays_race, type='python')
            bot.full_clean()
            bot.save()
            CompetitionParticipation.objects.create(bot_id=bot.id, competition_id=competition_id)
            return bot

    @FakeRedis("django_redis.get_redis_connection")
    def _post_to_matches(self):
        return self.client.post('/api/arenaclient/matches/')

    @FakeRedis("django_redis.get_redis_connection")
    def _post_to_results_custom(self, match_id, result_type, replay_file, bot1_data, bot2_data, bot1_log, bot2_log,
                                arenaclient_log):
        return self.client.post('/api/arenaclient/results/',
                                {'match': match_id,
                                 'type': result_type,
                                 'replay_file': replay_file,
                                 'game_steps': 500,
                                 'bot1_data': bot1_data,
                                 'bot2_data': bot2_data,
                                 'bot1_log': bot1_log,
                                 'bot2_log': bot2_log,
                                 'bot1_avg_step_time': 0.2,
                                 'bot2_avg_step_time': 0.1,
                                 'arenaclient_log': arenaclient_log})

    @FakeRedis("django_redis.get_redis_connection")
    def _post_to_results(self, match_id, result_type):
        """
        Posts a generic result.
        :param match_id:
        :param result_type:
        :return:
        """
        filename = os.path.join(os.path.dirname(os.path.realpath(__file__)),
                                'test-media/../test-media/testReplay.SC2Replay')
        with open(filename, 'rb') as replay_file, open(self.test_bot_datas['bot1'][0]['path'], 'rb') as bot1_data, open(
                self.test_bot_datas['bot2'][0]['path'], 'rb') as bot2_data, open(self.test_bot1_match_log_path,
                                                                    'rb') as bot1_log, open(
            self.test_bot2_match_log_path, 'rb') as bot2_log, open(self.test_arenaclient_log_path,
                                                                   'rb') as arenaclient_log:
            return self._post_to_results_custom(match_id, result_type, replay_file, bot1_data, bot2_data, bot1_log, bot2_log, arenaclient_log)

    @FakeRedis("django_redis.get_redis_connection")
    def _post_to_results_bot_datas_set_1(self, match_id, result_type):
        """
        Posts a generic result, using bot datas of index 1.
        :param match_id:
        :param result_type:
        :return:
        """
        filename = os.path.join(os.path.dirname(os.path.realpath(__file__)),
                                'test-media/../test-media/testReplay.SC2Replay')
        with open(filename, 'rb') as replay_file, open(self.test_bot_datas['bot1'][1]['path'], 'rb') as bot1_data, open(
                self.test_bot_datas['bot2'][1]['path'], 'rb') as bot2_data, open(self.test_bot1_match_log_path,
                                                                    'rb') as bot1_log, open(
            self.test_bot2_match_log_path, 'rb') as bot2_log, open(self.test_arenaclient_log_path,
                                                                   'rb') as arenaclient_log:
            return self._post_to_results_custom(match_id, result_type, replay_file, bot1_data, bot2_data, bot1_log, bot2_log, arenaclient_log)

    @FakeRedis("django_redis.get_redis_connection")
    def _post_to_results_no_bot_datas(self, match_id, result_type):
        filename = os.path.join(os.path.dirname(os.path.realpath(__file__)),
                                'test-media/../test-media/testReplay.SC2Replay')
        with open(filename, 'rb') as replayFile:
            return self.client.post('/api/arenaclient/results/',
                                    {'match': match_id,
                                     'type': result_type,
                                     'replay_file': SimpleUploadedFile("replayFile.SC2Replay", replayFile.read()),
                                     'game_steps': 500})

    @FakeRedis("django_redis.get_redis_connection")
    def _post_to_results_no_bot1_data(self, match_id, result_type, bot_data_set):
        filename = os.path.join(os.path.dirname(os.path.realpath(__file__)),
                                'test-media/../test-media/testReplay.SC2Replay')
        with open(filename, 'rb') as replay_file, open(self.test_bot_datas['bot2'][bot_data_set]['path'], 'rb') as bot2_data:
            return self._post_to_results_custom(match_id, result_type, replay_file, '', bot2_data, '', '', '')

    @FakeRedis("django_redis.get_redis_connection")
    def _post_to_results_no_bot2_data(self, match_id, result_type, bot_data_set):
        filename = os.path.join(os.path.dirname(os.path.realpath(__file__)),
                                'test-media/../test-media/testReplay.SC2Replay')
        with open(filename, 'rb') as replay_file, open(self.test_bot_datas['bot1'][bot_data_set]['path'], 'rb') as bot1_data:
            return self._post_to_results_custom(match_id, result_type, replay_file, bot1_data, '', '', '', '')

    @FakeRedis("django_redis.get_redis_connection")
    def _post_to_results_no_replay(self, match_id, result_type):
        return self.client.post('/api/arenaclient/results/',
                                {'match': match_id,
                                 'type': result_type,
                                 'replay_file': '',
                                 'game_steps': 500})

    @FakeRedis("django_redis.get_redis_connection")
    def _post_to_results_no_replay_updated_datas(self, match_id, result_type):
        filename = os.path.join(os.path.dirname(os.path.realpath(__file__)),
                                'test-media/../test-media/testReplay.SC2Replay')
        with open(filename, 'rb') as replayFile, open(self.test_bot_datas['bot1'][0]['path'], 'rb') as bot2_data, open(
                self.test_bot_datas['bot2'][0]['path'], 'rb') as bot1_data, open(self.test_bot1_match_log_path,
                                                                    'rb') as bot1_log, open(
            self.test_bot2_match_log_path, 'rb') as bot2_log, open(self.test_arenaclient_log_path,
                                                                   'rb') as arenaclient_log:
            return self.client.post('/api/arenaclient/results/',
                                    {'match': match_id,
                                     'type': result_type,
                                     'replay_file': '',
                                     'game_steps': 500,
                                     'bot1_data': SimpleUploadedFile("bot1_data.zip", bot1_data.read()),
                                     'bot2_data': SimpleUploadedFile("bot2_data.zip", bot2_data.read()),
                                     'bot1_log': SimpleUploadedFile("bot1_log.zip", bot1_log.read()),
                                     'bot2_log': SimpleUploadedFile("bot2_log.zip", bot2_log.read()),
                                     })

    @FakeRedis("django_redis.get_redis_connection")
    def _generate_full_data_set(self):
        self.test_client.login(User.objects.get(username='staff_user'))

        self._generate_extra_users()
        self._generate_extra_bots()

        self._generate_match_activity()

        # generate a bot match request to ensure it doesn't bug things out
        from aiarena.core.api import Bots  # avoid circular reference
        game_mode = GameMode.objects.get(name='Melee')
        bots = Bots.get_available(Bot.objects.all())
        Matches.request_match(self.regularUser2, bots[0], bots[0].get_random_active_excluding_self(), game_mode=game_mode)

        # generate match requests from regularUser1
        bot = Bot.get_random_active()
        Matches.request_match(self.regularUser1, bot, bot.get_random_active_excluding_self(), game_mode=game_mode)
        Matches.request_match(self.regularUser1, bot, bot.get_random_active_excluding_self(), game_mode=game_mode)
        bot = Bot.get_random_active()
        Matches.request_match(self.regularUser1, bot, bot.get_random_active_excluding_self(), game_mode=game_mode)

        self.test_client.logout()  # child tests can login if they require

    @FakeRedis("django_redis.get_redis_connection")
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
        response = self._post_to_results_no_bot1_data(response.data['id'], 'Player1Win', 0)
        self.assertEqual(response.status_code, 201)

        response = self._post_to_matches()
        self.assertEqual(response.status_code, 201)
        response = self._post_to_results_no_bot2_data(response.data['id'], 'Player1Crash', 0)
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

    @FakeRedis("django_redis.get_redis_connection")
    def _generate_extra_bots(self):
        competition = Competition.objects.get()
        self.regularUser2Bot1 = self._create_bot(self.regularUser2, 'regularUser2Bot1')
        self.regularUser2Bot2 = self._create_active_bot_for_competition(competition.id, self.regularUser2, 'regularUser2Bot2')
        self.regularUser3Bot1 = self._create_active_bot_for_competition(competition.id, self.regularUser3, 'regularUser3Bot1')
        self.regularUser3Bot2 = self._create_active_bot_for_competition(competition.id, self.regularUser3, 'regularUser3Bot2', 'Z')
        self.regularUser4Bot1 = self._create_bot(self.regularUser4, 'regularUser4Bot1')
        self.regularUser4Bot2 = self._create_bot(self.regularUser4, 'regularUser4Bot2')

    @FakeRedis("django_redis.get_redis_connection")
    def _generate_extra_users(self):
        self.regularUser2 = User.objects.create_user(username='regular_user2', password='x',
                                                     email='regular_user2@dev.aiarena.net')
        self.regularUser3 = User.objects.create_user(username='regular_user3', password='x',
                                                     email='regular_user3@dev.aiarena.net')
        self.regularUser4 = User.objects.create_user(username='regular_user4', password='x',
                                                     email='regular_user4@dev.aiarena.net')


class LoggedInMixin(BaseTestMixin):
    """
    A test case for when logged in as a user.
    """

    @FakeRedis("django_redis.get_redis_connection")
    def setUp(self):
        super().setUp()
        self.staffUser1 = User.objects.create_user(username='staff_user', password='x',
                                                   email='staff_user@dev.aiarena.net',
                                                   is_staff=True,
                                                   is_superuser=True,
                                                   is_active=True)

        self.arenaclientUser1 = ArenaClient.objects.create(username='arenaclient1', email='arenaclient@dev.aiarena.net',
                                                         type='ARENA_CLIENT', trusted=True, owner=self.staffUser1)
        Token.objects.create(user=self.arenaclientUser1)

        self.regularUser1 = User.objects.create_user(username='regular_user1', password='x',
                                                     email='regular_user1@dev.aiarena.net')


class MatchReadyMixin(LoggedInMixin):
    """
    A test case which is setup and ready to run matches
    """

    @FakeRedis("django_redis.get_redis_connection")
    def setUp(self):
        super().setUp()

        # raise the configured per user limits
        config.MAX_USER_BOT_PARTICIPATIONS_ACTIVE_FREE_TIER = 10
        config.MAX_USER_BOT_COUNT = 10

        self.test_client.login(self.staffUser1)
        competition = self._create_game_mode_and_open_competition()
        self._create_map_for_competition('testmap1', competition.id)

        self.regularUser1Bot1 = self._create_active_bot_for_competition(competition.id, self.regularUser1, 'regularUser1Bot1', 'T')
        self.regularUser1Bot2 = self._create_active_bot_for_competition(competition.id, self.regularUser1, 'regularUser1Bot2', 'Z')
        self.regularUser1Bot2 = self._create_bot(self.regularUser1, 'regularUser1Bot3', 'P')  # inactive bot for realism
        self.staffUser1Bot1 = self._create_active_bot_for_competition(competition.id, self.staffUser1, 'staffUser1Bot1', 'T')
        self.staffUser1Bot2 = self._create_active_bot_for_competition(competition.id, self.staffUser1, 'staffUser1Bot2', 'Z')


# Use this to pre-build a fuller dataset for testing
class FullDataSetMixin(MatchReadyMixin):
    """
    A test case with a full dataset including run matches.
    """

    @FakeRedis("django_redis.get_redis_connection")
    def setUp(self):
        super().setUp()
        self._generate_full_data_set()


class UtilsTestCase(BaseTestMixin, TestCase):
    @FakeRedis("django_redis.get_redis_connection")
    def test_calc_md5(self):
        filename = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'test-media/../test-media/test_bot.zip')
        self.assertEqual('c96bcfc79318a8b50b0b2c8696400d06', calculate_md5(filename))


class BotTestCase(LoggedInMixin, TestCase):

    @FakeRedis("django_redis.get_redis_connection")
    def test_bot_creation_and_update(self):
        # set the configured per user limits for this test
        config.MAX_USER_BOT_PARTICIPATIONS_ACTIVE = 1
        config.MAX_USER_BOT_COUNT = 4

        self.test_client.login(self.staffUser1)

        # required for active bot
        competition = self._create_game_mode_and_open_competition()

        # create active bot along with bot data
        with open(self.test_bot_zip_path, 'rb') as bot_zip, open(self.test_bot_datas['bot1'][0]['path'], 'rb') as bot_data:
            bot1 = Bot(user=self.regularUser1, name='testbot', bot_zip=File(bot_zip), bot_data=File(bot_data),
                       plays_race='T', type='python')
            bot1.full_clean()
            bot1.save()
            CompetitionParticipation.objects.create(competition=competition, bot=bot1, active=True)


        # test display id regen
        prev_bot_display_id = bot1.game_display_id
        bot1.regen_game_display_id()
        self.assertNotEqual(bot1.game_display_id, prev_bot_display_id)

        bot1.refresh_from_db()
        # check hashes
        self.assertEqual(self.test_bot_zip_hash, bot1.bot_zip_md5hash)
        self.assertEqual(self.test_bot_datas['bot1'][0]['hash'], bot1.bot_data_md5hash)

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
        # this shouldn't trip the validation
        inactive_bot = Bot.objects.filter(user=self.regularUser1, competition_participations__isnull=True).first()
        cp = CompetitionParticipation.objects.create(competition=competition, bot=inactive_bot, active=False)
        cp.full_clean()

        # this should trip the validation
        with self.assertRaisesMessage(ValidationError,
                                      'Too many active participations already exist for this user.'
                                      ' You are allowed 1 active participations in competitions.'):
            cp = CompetitionParticipation.objects.create(competition=competition, bot=inactive_bot, active=True)
            cp.full_clean()

        # test updating bot_zip
        with open(self.test_bot_zip_updated_path, 'rb') as bot_zip_updated:
            bot1.bot_zip = File(bot_zip_updated)
            bot1.save()

        bot1.refresh_from_db()
        self.assertEqual(self.test_bot_zip_updated_hash, bot1.bot_zip_md5hash)

        # test updating bot_data
        # using bot2's data instead here so it's different
        with open(self.test_bot_datas['bot2'][0]['path'], 'rb') as bot_data_updated:
            bot1.bot_data = File(bot_data_updated)
            bot1.save()

        bot1.refresh_from_db()
        self.assertEqual(self.test_bot_datas['bot2'][0]['hash'], bot1.bot_data_md5hash)


class CompetitionsTestCase(FullDataSetMixin, TransactionTestCase):
    """
    Test competition rotation
    """

    @FakeRedis("django_redis.get_redis_connection")
    def _finish_competition_rounds(self):
        for x in range(Match.objects.filter(result__isnull=True).count()):
            response = self._post_to_matches()
            self.assertEqual(response.status_code, 201)

            response = self._post_to_results(response.data['id'], 'Player1Win')
            self.assertEqual(response.status_code, 201)

    @FakeRedis("django_redis.get_redis_connection")
    def test_competition_states(self):
        self.client.force_login(self.arenaclientUser1)

        self.assertEqual(Match.objects.filter(result__isnull=True).count(), 15,
                         msg='This test expects 15 unplayed matches in order to work.')

        # cache the bots - list forces the queryset to be evaluated
        bots = list(Bot.objects.all())

        competition1 = Competition.objects.get()

        # start a new round
        # response = self._post_to_matches()
        # self.assertEqual(response.status_code, 201)

        # Freeze the competition - now we shouldn't receive any new matches
        competition1.freeze()

        response = self._post_to_matches()
        self.assertEqual(response.status_code, 200)
        self.assertEqual(u'There are no currently available competitions.', response.data['detail'])

        # Pause the competition and finish the round
        competition1.pause()

        self._finish_competition_rounds()

        # this should fail due to a new round trying to generate while the competition is paused
        response = self._post_to_matches()
        self.assertEqual(response.status_code, 200)
        self.assertEqual(u'The competition is paused.', response.data['detail'])

        # reopen the competition
        competition1.open()

        # start a new round
        response = self._post_to_matches()
        self.assertEqual(response.status_code, 201)

        competition1.start_closing()

        # Activating a bot should now fail
        with self.assertRaisesMessage(ValidationError, 'That competition is not accepting new participants.'):
            bot = Bot.objects.filter(competition_participations__isnull=True).first()
            cp = CompetitionParticipation(competition=competition1, bot=bot)
            cp.full_clean()  # causes validation to run

        # finish the competition
        self._finish_competition_rounds()

        # successful close
        competition1.refresh_from_db()
        self.assertEqual(competition1.status, 'closed')

        # Activating a bot should fail
        with self.assertRaisesMessage(ValidationError, 'That competition is not accepting new participants.'):
            bot = Bot.objects.filter(competition_participations__isnull=True).first()
            cp = CompetitionParticipation(competition=competition1, bot=bot)
            cp.full_clean()  # causes validation to run

        # start a new competition
        competition2 = Competition.objects.create(game_mode=GameMode.objects.first())

        # no currently available competitions
        response = self._post_to_matches()
        self.assertEqual(response.status_code, 200)
        self.assertEqual(u'There are no currently available competitions.',
                         response.data['detail'])

        # active bots
        for bot in Bot.objects.all():
            CompetitionParticipation.objects.create(bot=bot, competition=competition2)

        # current competition is paused
        response = self._post_to_matches()
        self.assertEqual(response.status_code, 200)
        self.assertEqual(u'There are no currently available competitions.', response.data['detail'])

        competition2.open()

        # check no bot display IDs have changed
        # they used to change in previous website versions - make sure they no longer do
        for bot in bots:
            updated_bot = Bot.objects.get(id=bot.id)
            self.assertEqual(updated_bot.game_display_id, bot.game_display_id)

        # no maps
        response = self._post_to_matches()
        self.assertEqual(response.status_code, 200)
        self.assertEqual(u'no_maps', response.data['detail'].code)

        map = Map.objects.first()
        map.competitions.add(competition2)

        # start a new round
        response = self._post_to_matches()
        self.assertEqual(response.status_code, 201)

        # New round should be number 1 for the new competition
        round = Round.objects.get(competition=competition2)
        self.assertEqual(round.number, 1)


class ManagementCommandTests(MatchReadyMixin, TransactionTestCase):
    """
    Tests for management commands
    """

    @FakeRedis("django_redis.get_redis_connection")
    def test_cancel_matches(self):
        count = CompetitionParticipation.objects.filter(active=True).count()
        expectedMatchCountPerRound = int(count / 2 * (count - 1))

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

    @FakeRedis("django_redis.get_redis_connection")
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
            'Cleaning up replays starting from 30 days into the past...\nGathering records to clean...\n{0} records gathered.\nCleaned up {0} replays.'.format(NUM_MATCHES),
            out.getvalue())

        # ensure the job doesn't re-clean the same records when run again
        out = StringIO()
        call_command('cleanupreplays', stdout=out)
        self.assertIn(
            'Cleaning up replays starting from 30 days into the past...\nGathering records to clean...\n0 records gathered.\nCleaned up 0 replays.',
            out.getvalue())

        self.assertEqual(results.count(), NUM_MATCHES)
        for result in results:
            self.assertFalse(result.replay_file)

        out = StringIO()
        call_command('cleanuparenaclientlogfiles', stdout=out)
        self.assertIn(
            'Cleaning up arena client logfiles starting from 30 days into the past...\nGathering records to clean...\n{0} records gathered.\nCleaned up {0} logfiles.'.format(
                NUM_MATCHES),
            out.getvalue())

        # ensure the job doesn't re-clean the same records when run again
        out = StringIO()
        call_command('cleanuparenaclientlogfiles', stdout=out)
        self.assertIn(
            'Cleaning up arena client logfiles starting from 30 days into the past...\nGathering records to clean...\n0 records gathered.\nCleaned up 0 logfiles.',
            out.getvalue())

        self.assertEqual(results.count(), NUM_MATCHES)
        for result in results:
            self.assertFalse(result.replay_file)

        out = StringIO()
        call_command('cleanupmatchlogfiles', stdout=out)
        self.assertIn(
            'Cleaning up match logfiles starting from 30 days into the past...\nGathering records to clean...\n{0} records gathered.\nCleaned up {0} logfiles.'.format(
                NUM_MATCHES * 2),
            out.getvalue())

        # ensure the job doesn't re-clean the same records when run again
        out = StringIO()
        call_command('cleanupmatchlogfiles', stdout=out)
        self.assertIn(
            'Cleaning up match logfiles starting from 30 days into the past...\nGathering records to clean...\n0 records gathered.\nCleaned up 0 logfiles.',
            out.getvalue())

        self.assertEqual(participants.count(), NUM_MATCHES * 2)
        for participant in participants:
            self.assertFalse(participant.match_log)

    @FakeRedis("django_redis.get_redis_connection")
    def test_generatestats(self):
        self._generate_full_data_set()
        out = StringIO()
        call_command('generatestats', stdout=out)
        self.assertIn('Done', out.getvalue())

    @FakeRedis("django_redis.get_redis_connection")
    def test_generatestats_competition(self):
        self._generate_full_data_set()
        out = StringIO()
        call_command('generatestats', '--competitionid', '1', stdout=out)
        self.assertIn('Done', out.getvalue())

    @FakeRedis("django_redis.get_redis_connection")
    def test_generatestats_bot(self):
        self._generate_full_data_set()
        out = StringIO()
        call_command('generatestats', '--botid', '1', stdout=out)
        self.assertIn('Done', out.getvalue())

    @FakeRedis("django_redis.get_redis_connection")
    def test_seed(self):
        out = StringIO()
        call_command('seed', stdout=out)
        self.assertIn('Done. User logins have a password of "x".', out.getvalue())

    @FakeRedis("django_redis.get_redis_connection")
    def test_check_bot_hashes(self):
        call_command('checkbothashes')

    @FakeRedis("django_redis.get_redis_connection")
    def test_repair_bot_hashes(self):
        call_command('repairbothashes')

    @FakeRedis("django_redis.get_redis_connection")
    def test_timeout_overtime_matches(self):
        self.client.force_login(User.objects.get(username='arenaclient1'))

        response = self.client.post('/api/arenaclient/matches/')
        self.assertEqual(response.status_code, 201)

        # save the match for modification
        match1 = Match.objects.get(id=response.data['id'])

        # set the created time back into the past long enough for it to cause a time out
        match1.started = timezone.now() - (config.TIMEOUT_MATCHES_AFTER + timedelta(hours=1))
        match1.save()

        # this should trigger the bots to be forced out of the match
        call_command('timeoutovertimematches')

        # confirm a result was registered
        self.assertTrue(match1.result is not None)
