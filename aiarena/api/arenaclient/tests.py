import os

from constance import config
from django.db.models import Sum
from django.test import TransactionTestCase

from aiarena.core.api import Matches
from aiarena.core.models import Match, Bot, MatchParticipation, User, Round, Result, SeasonParticipation, Season, Map, \
    ArenaClient
from aiarena.core.tests.tests import LoggedInMixin, MatchReadyMixin
from aiarena.core.utils import calculate_md5
from aiarena.settings import ELO_START_VALUE, BASE_DIR, PRIVATE_STORAGE_ROOT, MEDIA_ROOT


class MatchesTestCase(LoggedInMixin, TransactionTestCase):
    def setUp(self):
        super(MatchesTestCase, self).setUp()
        self.regularUser2 = User.objects.create_user(username='regular_user2', password='x',
                                                     email='regular_user2@aiarena.net')

    def test_get_next_match_not_authorized(self):
        response = self._post_to_matches()
        self.assertEqual(response.status_code, 403)

        self.client.login(username='regular_user', password='x')
        response = self._post_to_matches()
        self.assertEqual(response.status_code, 403)

    def test_post_next_match(self):
        # avoid old tests breaking that were pre-this feature
        config.REISSUE_UNFINISHED_MATCHES = False

        self.client.force_login(User.objects.get(username='arenaclient1'))

        # no current season
        response = self._post_to_matches()
        self.assertEqual(response.status_code, 200)

        # needs a valid season to be able to activate a bot.
        self._create_open_season()

        # no maps
        response = self._post_to_matches()
        self.assertEqual(response.status_code, 200)

        # not enough active bots
        self._create_map('test_map')
        response = self._post_to_matches()
        self.assertEqual(response.status_code, 200)

        # not enough active bots
        bot1 = self._create_bot(self.regularUser1, 'testbot1')
        response = self._post_to_matches()
        self.assertEqual(response.status_code, 200)

        # not enough active bots
        bot2 = self._create_bot(self.regularUser1, 'testbot2')
        response = self._post_to_matches()
        self.assertEqual(response.status_code, 200)

        # not enough active bots
        bot1.active = True
        bot1.save()
        response = self._post_to_matches()
        self.assertEqual(response.status_code, 200)

        # success
        bot2.active = True
        bot2.save()
        response = self._post_to_matches()
        self.assertEqual(response.status_code, 201)

        # test download files

        # zip
        bot1_zip = self.client.get(response.data['bot1']['bot_zip'])
        bot1_zip_path = "./tmp/bot1.zip"
        with open(bot1_zip_path, "wb") as bot1_zip_file:  # todo: this can probably be done without saving to file
            bot1_zip_file.write(bot1_zip.content)
            bot1_zip_file.close()
        self.assertEqual(response.data['bot1']['bot_zip_md5hash'], calculate_md5(bot1_zip_path))

        bot1_zip = self.client.get(response.data['bot2']['bot_zip'])
        bot1_zip_path = "./tmp/bot2.zip"
        with open(bot1_zip_path, "wb") as bot1_zip_file:
            bot1_zip_file.write(bot1_zip.content)
            bot1_zip_file.close()
        self.assertEqual(response.data['bot2']['bot_zip_md5hash'], calculate_md5(bot1_zip_path))

        # data
        bot1_zip = self.client.get(response.data['bot1']['bot_data'])
        bot1_zip_path = "./tmp/bot1_data.zip"
        with open(bot1_zip_path, "wb") as bot1_zip_file:
            bot1_zip_file.write(bot1_zip.content)
            bot1_zip_file.close()
        self.assertEqual(response.data['bot1']['bot_data_md5hash'], calculate_md5(bot1_zip_path))

        bot1_zip = self.client.get(response.data['bot2']['bot_data'])
        bot1_zip_path = "./tmp/bot2_data.zip"
        with open(bot1_zip_path, "wb") as bot1_zip_file:
            bot1_zip_file.write(bot1_zip.content)
            bot1_zip_file.close()
        self.assertEqual(response.data['bot2']['bot_data_md5hash'], calculate_md5(bot1_zip_path))

        # not enough available bots
        response = self._post_to_matches()
        self.assertEqual(response.status_code, 200)

        # ensure only 1 match was created
        self.assertEqual(Match.objects.count(), 1)


    def test_match_reissue(self):

        self.client.force_login(User.objects.get(username='arenaclient1'))
        self._create_map('test_map')
        self._create_open_season()

        self._create_active_bot(self.regularUser1, 'testbot1', 'T')
        self._create_active_bot(self.regularUser1, 'testbot2', 'Z')

        response_m1 = self.client.post('/api/arenaclient/matches/')
        self.assertEqual(response_m1.status_code, 201)

        # should be the same match reissued
        response_m2 = self.client.post('/api/arenaclient/matches/')
        self.assertEqual(response_m2.status_code, 201)

        self.assertEqual(response_m1.data['id'], response_m2.data['id'])

    def test_max_active_rounds(self):
        # we don't want to have to create lots of arenaclients for multiple matches
        config.REISSUE_UNFINISHED_MATCHES = False
        config.MAX_ACTIVE_ROUNDS = 2

        self.client.force_login(User.objects.get(username='arenaclient1'))
        self._create_map('test_map')
        self._create_open_season()

        bot1 = self._create_active_bot(self.regularUser1, 'testbot1', 'T')
        bot2 = self._create_active_bot(self.regularUser1, 'testbot2', 'Z')
        bot3 = self._create_active_bot(self.regularUser1, 'testbot3', 'P')
        bot4 = self._create_active_bot(self.regularUser1, 'testbot4', 'R')

        # Round 1
        response = self.client.post('/api/arenaclient/matches/')
        self.assertEqual(response.status_code, 201)
        response = self.client.post('/api/arenaclient/matches/')
        self.assertEqual(response.status_code, 201)
        response = self._post_to_results(response.data['id'], 'Player1Win')
        self.assertEqual(response.status_code, 201)

        # Match 1 has started, Match 2 is finished.

        # Round 2
        response = self.client.post('/api/arenaclient/matches/')
        self.assertEqual(response.status_code, 201)
        response = self._post_to_results(response.data['id'], 'Player1Win')
        self.assertEqual(response.status_code, 201)

        # Round 3 - should fail due to active round limit
        response = self.client.post('/api/arenaclient/matches/')
        self.assertEqual(response.status_code, 200)
        self.assertTrue('detail' in response.data)
        self.assertEqual(u'There are available bots, but the ladder has reached the maximum active rounds allowed and ' \
                         'serving a new match would require generating a new one. Please wait until matches from current ' \
                         'rounds become available.',
                         response.data['detail'])

    def test_match_blocking(self):
        # create an extra arena client for this test
        self.arenaclientUser2 = ArenaClient.objects.create(username='arenaclient2', email='arenaclient2@dev.aiarena.net',
                                                         type='ARENA_CLIENT', trusted=True, owner=self.staffUser1)

        self.client.force_login(User.objects.get(username='arenaclient1'))
        self._create_map('test_map')
        self._create_open_season()

        bot1 = self._create_active_bot(self.regularUser1, 'testbot1', 'T')
        bot2 = self._create_active_bot(self.regularUser1, 'testbot2', 'Z')

        # this should tie up both bots
        response = self.client.post('/api/arenaclient/matches/')
        self.assertEqual(response.status_code, 201)

        # we shouldn't be able to get a new match
        self.client.force_login(User.objects.get(username='arenaclient2'))
        response = self.client.post('/api/arenaclient/matches/')
        self.assertEqual(response.status_code, 500)
        self.assertEqual(u"Failed to start match. There might not be any available participants.", response.data['detail'])

        Matches.request_match(self.regularUser2, bot1, bot1.get_random_active_excluding_self())

        # now we should be able to get a match - the requested one
        response = self.client.post('/api/arenaclient/matches/')
        self.assertEqual(response.status_code, 201)



class ResultsTestCase(LoggedInMixin, TransactionTestCase):
    uploaded_bot_data_path = os.path.join(BASE_DIR, PRIVATE_STORAGE_ROOT, 'bots', '{0}', 'bot_data')
    uploaded_bot_data_backup_path = os.path.join(BASE_DIR, PRIVATE_STORAGE_ROOT, 'bots', '{0}', 'bot_data_backup')
    uploaded_match_log_path = os.path.join(BASE_DIR, PRIVATE_STORAGE_ROOT, 'match-logs', '{0}')
    uploaded_arenaclient_log_path = os.path.join(MEDIA_ROOT, 'arenaclient-logs', '{0}_arenaclientlog.zip')

    def test_create_results(self):
        self.client.force_login(User.objects.get(username='arenaclient1'))

        self._create_map('test_map')
        self._create_open_season()

        bot1 = self._create_active_bot(self.regularUser1, 'bot1')
        bot2 = self._create_active_bot(self.regularUser1, 'bot2', 'Z')

        # post a standard result
        response = self._post_to_matches()
        self.assertEqual(response.status_code, 201)
        match = response.data
        response = self._post_to_results(match['id'], 'Player1Win')
        self.assertEqual(response.status_code, 201)

        p1 = MatchParticipation.objects.get(match_id=match['id'], participant_number=1)
        p2 = MatchParticipation.objects.get(match_id=match['id'], participant_number=2)

        # check bot datas exist
        self.assertTrue(os.path.exists(self.uploaded_bot_data_path.format(bot1.id)))
        self.assertTrue(os.path.exists(self.uploaded_bot_data_path.format(bot2.id)))

        # check hashes match set 0
        self._check_hashes(bot1, bot2, match['id'], 0)

        # check match logs exist
        self.assertTrue(os.path.exists(self.uploaded_arenaclient_log_path.format(match['id'])))
        self.assertTrue(os.path.exists(self.uploaded_match_log_path.format(p1.id)))
        self.assertTrue(os.path.exists(self.uploaded_match_log_path.format(p2.id)))

        # Post a result with different bot datas
        response = self._post_to_matches()
        self.assertEqual(response.status_code, 201)
        match = response.data
        self._post_to_results_bot_datas_set_1(match['id'], 'Player1Win')
        self.assertEqual(response.status_code, 201)

        # check bot datas and their backups exist
        self.assertTrue(os.path.exists(self.uploaded_bot_data_path.format(bot1.id)))
        self.assertTrue(os.path.exists(self.uploaded_bot_data_path.format(bot2.id)))
        self.assertTrue(os.path.exists(self.uploaded_bot_data_backup_path.format(bot1.id)))
        self.assertTrue(os.path.exists(self.uploaded_bot_data_backup_path.format(bot2.id)))

        # check hashes - should be updated to set 1
        self._check_hashes(bot1, bot2, match['id'], 1)

        # check match logs exist
        self.assertTrue(os.path.exists(self.uploaded_match_log_path.format(match['id'])))
        self.assertTrue(os.path.exists(self.uploaded_match_log_path.format(p1.id)))
        self.assertTrue(os.path.exists(self.uploaded_match_log_path.format(p2.id)))

        # post a standard result with no bot1 data
        match = self._post_to_matches().data
        response = self._post_to_results_no_bot1_data(match['id'], 'Player1Win', 1)
        self.assertEqual(response.status_code, 201)

        # check hashes - nothing should have changed
        self._check_hashes(bot1, bot2, match['id'], 1)

        # ensure no files got wiped
        self.assertTrue(Bot.objects.get(id=bot1.id).bot_data)
        self.assertTrue(Bot.objects.get(id=bot2.id).bot_data)

        # post a standard result with no bot2 data
        match = self._post_to_matches().data
        response = self._post_to_results_no_bot2_data(match['id'], 'Player1Win', 1)
        self.assertEqual(response.status_code, 201)

        # check hashes - nothing should have changed
        self._check_hashes(bot1, bot2, match['id'], 1)

        # test that requested matches don't update bot_data
        match5 = Matches.request_match(self.staffUser1, bot1, bot2, Map.random_active())
        self._post_to_results_bot_datas_set_1(match5.id, 'Player1Win')

        # check hashes - nothing should have changed
        self._check_hashes(bot1, bot2, match5.id, 1)

        # post a win without a replay - should fail
        match = self._post_to_matches().data
        response = self._post_to_results_no_replay(match['id'], 'Player2Win')
        self.assertEqual(response.status_code, 400)
        self.assertTrue('non_field_errors' in response.data)
        self.assertEqual(response.data['non_field_errors'][0],
                         'A win/loss or tie result must be accompanied by a replay file.')

        # no hashes should have changed
        self._check_hashes(bot1, bot2, match['id'], 1)

    def _check_hashes(self, bot1, bot2, match_id, data_index):
        # check hashes - nothing should have changed
        match_bot = MatchParticipation.objects.get(bot=bot1,
                                                   match_id=match_id)  # use this to determine which hash to match
        if match_bot.participant_number == 1:
            self.assertEqual(self.test_bot_datas['bot1'][data_index]['hash'], Bot.objects.get(id=bot1.id).bot_data_md5hash)
            self.assertEqual(self.test_bot_datas['bot2'][data_index]['hash'], Bot.objects.get(id=bot2.id).bot_data_md5hash)
        else:
            self.assertEqual(self.test_bot_datas['bot1'][data_index]['hash'], Bot.objects.get(id=bot2.id).bot_data_md5hash)
            self.assertEqual(self.test_bot_datas['bot2'][data_index]['hash'], Bot.objects.get(id=bot1.id).bot_data_md5hash)

    def test_create_result_bot_not_in_match(self):
        self.client.force_login(User.objects.get(username='arenaclient1'))

        self._create_map('test_map')
        self._create_open_season()

        # Create 3 bots, so after a round is generated, we'll have some unstarted matches
        bot1 = self._create_active_bot(self.regularUser1, 'bot1')
        bot2 = self._create_active_bot(self.regularUser1, 'bot2', 'Z')
        bot3 = self._create_active_bot(self.regularUser1, 'bot3', 'P')
        response = self._post_to_matches()
        self.assertEqual(response.status_code, 201)
        match = response.data

        not_started_match = Match.objects.filter(started__isnull=True, result__isnull=True).first()

        # should fail
        response = self._post_to_results(not_started_match.id, 'Player1Win')
        self.assertEqual(response.status_code, 500)
        self.assertTrue('detail' in response.data)
        self.assertEqual(u'Unable to log result: Bot bot1 is not currently in this match!',
                         response.data['detail'])

    def test_get_results_not_authorized(self):
        response = self.client.get('/api/arenaclient/results/')
        self.assertEqual(response.status_code, 403)

        self.client.login(username='regular_user', password='x')
        response = self.client.get('/api/arenaclient/results/')
        self.assertEqual(response.status_code, 403)

    def test_bot_disable_on_consecutive_crashes(self):
        # This is the feature we're testing, so turn it on
        config.BOT_CONSECUTIVE_CRASH_LIMIT = 3  # todo: this update doesn't work.

        self.client.force_login(User.objects.get(username='arenaclient1'))

        self._create_map('test_map')
        self._create_open_season()

        bot1 = self._create_active_bot(self.regularUser1, 'bot1')
        bot2 = self._create_active_bot(self.regularUser1, 'bot2', 'Z')

        # log more crashes than should be allowed
        for count in range(config.BOT_CONSECUTIVE_CRASH_LIMIT):
            response = self._post_to_matches()
            self.assertEqual(response.status_code, 201)
            match = response.data
            # always make the same bot crash
            if match['bot1']['name'] == bot1.name:
                response = self._post_to_results(match['id'], 'Player1Crash')
            else:
                response = self._post_to_results(match['id'], 'Player2Crash')
            self.assertEqual(response.status_code, 201)

        # The bot should be disabled
        bot1.refresh_from_db()
        self.assertFalse(bot1.active)

        # not enough active bots
        response = self._post_to_matches()
        self.assertEqual(response.status_code, 200)

        # Post a successful match, then retry the crashes to make sure the previous ones don't affect the check
        bot1.active = True
        bot1.save()
        response = self._post_to_matches()
        self.assertEqual(response.status_code, 201)
        match = response.data
        response = self._post_to_results(match['id'], 'Player2Win')
        self.assertEqual(response.status_code, 201)

        # once again log more crashes than should be allowed
        for count in range(config.BOT_CONSECUTIVE_CRASH_LIMIT):
            response = self._post_to_matches()
            self.assertEqual(response.status_code, 201)
            match = response.data
            # always make the same bot crash
            if match['bot1']['name'] == bot1.name:
                response = self._post_to_results(match['id'], 'Player1Crash')
            else:
                response = self._post_to_results(match['id'], 'Player2Crash')
            self.assertEqual(response.status_code, 201)

        # The bot should be disabled
        bot1.refresh_from_db()
        self.assertFalse(bot1.active)

        # not enough active bots
        response = self._post_to_matches()
        self.assertEqual(response.status_code, 200)


class EloTestCase(LoggedInMixin, TransactionTestCase):
    """
    Tests to ensure ELO calculations run properly.
    """

    def setUp(self):
        super(EloTestCase, self).setUp()
        self.client.force_login(User.objects.get(username='arenaclient1'))

        self.regularUserBot1 = self._create_bot(self.regularUser1, 'regularUserBot1')
        self.regularUserBot2 = self._create_bot(self.regularUser1, 'regularUserBot2')
        self._create_map('testmap')
        self._create_open_season()

        # activate the required bots
        self.regularUserBot1.active = True
        self.regularUserBot1.save()
        self.regularUserBot2.active = True
        self.regularUserBot2.save()

        # expected_win_sequence and expected_resultant_elos should have this many entries
        self.num_matches_to_play = 20

        self.expected_result_sequence = [
            self.regularUserBot1.id,
            self.regularUserBot2.id,
            self.regularUserBot1.id,
            self.regularUserBot1.id,
            self.regularUserBot1.id,
            'Tie',
            'Tie',
            self.regularUserBot2.id,
            'Tie',
            self.regularUserBot2.id,
            self.regularUserBot1.id,
            self.regularUserBot1.id,
            self.regularUserBot1.id,
            self.regularUserBot2.id,
            self.regularUserBot1.id,
            self.regularUserBot1.id,
            'Tie',
            self.regularUserBot1.id,
            self.regularUserBot1.id,
            self.regularUserBot1.id,
        ]

        self.expected_resultant_elos = [
            [1604, 1596],
            [1600, 1600],
            [1604, 1596],
            [1608, 1592],
            [1612, 1588],
            [1612, 1588],
            [1612, 1588],
            [1608, 1592],
            [1608, 1592],
            [1604, 1596],
            [1608, 1592],
            [1612, 1588],
            [1616, 1584],
            [1612, 1588],
            [1616, 1584],
            [1620, 1580],
            [1620, 1580],
            [1624, 1576],
            [1627, 1573],
            [1630, 1570],
        ]

    def CreateMatch(self):
        response = self.client.post('/api/arenaclient/matches/')
        self.assertEqual(response.status_code, 201)
        return response.data

    def CreateResult(self, match_id, r_type):
        response = self._post_to_results(match_id, r_type)
        self.assertEqual(response.status_code, 201, response.data)

    def DetermineResultType(self, bot1_id, iteration):
        if self.expected_result_sequence[iteration] == 'Tie':
            return 'Tie'
        else:
            return 'Player1Win' if bot1_id == self.expected_result_sequence[iteration] else 'Player2Win'

    def CheckResultantElos(self, match_id, iteration):
        bot1_participant = MatchParticipation.objects.filter(match_id=match_id, bot_id=self.regularUserBot1.id)[0]
        bot2_participant = MatchParticipation.objects.filter(match_id=match_id, bot_id=self.regularUserBot2.id)[0]

        self.assertEqual(self.expected_resultant_elos[iteration][0], bot1_participant.resultant_elo)
        self.assertEqual(self.expected_resultant_elos[iteration][1], bot2_participant.resultant_elo)

    def CheckFinalElos(self):
        sp1 = self.regularUserBot1.current_season_participation()
        sp2 = self.regularUserBot2.current_season_participation()
        self.assertEqual(sp1.elo, self.expected_resultant_elos[self.num_matches_to_play - 1][0])
        self.assertEqual(sp2.elo, self.expected_resultant_elos[self.num_matches_to_play - 1][1])

    def CheckEloSum(self):
        sumElo = SeasonParticipation.objects.filter(season=Season.get_current_season()).aggregate(Sum('elo'))
        self.assertEqual(sumElo['elo__sum'],
                         ELO_START_VALUE * Bot.objects.all().count())  # starting ELO times number of bots

    def test_elo(self):
        for iteration in range(0, self.num_matches_to_play):
            match = self.CreateMatch()
            res = self.DetermineResultType(match['bot1']['id'], iteration)
            self.CreateResult(match['id'], res)
            self.CheckResultantElos(match['id'], iteration)

        self.CheckFinalElos()

        self.CheckEloSum()

    # an exception won't be raised from this - but a log entry will
    # this is only to ensure no other exception takes place
    def test_elo_sanity_check(self):
        # todo: test log file content
        # log_file = "./logs/aiarena.log"
        # os.remove(log_file)  # clean it

        # intentionally cause a sanity check failure
        self.regularUserBot1.elo = ELO_START_VALUE - 1
        self.regularUserBot1.save()

        response = self._post_to_matches()
        self.assertEqual(response.status_code, 201)
        self._post_to_results(response.data['id'], 'Player1Win')

        # with open(log_file, "r") as f:
        #     self.assertFalse("did not match expected value of" in f.read())


class RoundRobinGenerationTestCase(MatchReadyMixin, TransactionTestCase):
    def setUp(self):
        super(RoundRobinGenerationTestCase, self).setUp()
        self.client.force_login(User.objects.get(username='arenaclient1'))

    def test_round_robin_generation(self):
        # avoid old tests breaking that were pre-this feature
        config.REISSUE_UNFINISHED_MATCHES = False

        botCount = Bot.objects.filter(active=True).count()
        expectedMatchCountPerRound = int(botCount / 2 * (botCount - 1))
        self.assertGreater(botCount, 1)  # check we have more than 1 bot

        self.assertEqual(Match.objects.count(), 0)  # starting with 0 matches
        self.assertEqual(Round.objects.count(), 0)  # starting with 0 rounds

        response = self._post_to_matches()  # this should trigger a new round robin generation
        self.assertEqual(response.status_code, 201)

        # check match count
        self.assertEqual(Match.objects.count(), expectedMatchCountPerRound)

        # check round data
        self.assertEqual(Round.objects.count(), 1)
        round = Round.objects.get(id=1)
        self.assertIsNotNone(round.started)
        self.assertIsNone(round.finished)
        self.assertFalse(round.complete)

        # finish the initial match
        response = self._post_to_results(response.data['id'], 'Player1Win')
        self.assertEqual(response.status_code, 201)

        # start and finish all the rest of the generated matches
        for x in range(1, expectedMatchCountPerRound):
            response = self._post_to_matches()
            self.assertEqual(response.status_code, 201)
            response = self._post_to_results(response.data['id'], 'Player1Win')
            self.assertEqual(response.status_code, 201)
            # double check the match count
            self.assertEqual(Match.objects.filter(started__isnull=True).count(), expectedMatchCountPerRound - x - 1)

        # check round is finished
        self.assertEqual(Round.objects.count(), 1)
        round = Round.objects.get(id=1)
        self.assertIsNotNone(round.finished)
        self.assertTrue(round.complete)

        # Repeat again but with quirks

        response = self._post_to_matches()  # this should trigger another new round robin generation
        self.assertEqual(response.status_code, 201)

        # check match count
        self.assertEqual(Match.objects.count(), expectedMatchCountPerRound * 2)

        # check round data
        self.assertEqual(Round.objects.count(), 2)
        round = Round.objects.get(id=2)
        self.assertIsNotNone(round.started)
        self.assertIsNone(round.finished)
        self.assertFalse(round.complete)

        # finish the initial match
        response = self._post_to_results(response.data['id'], 'Player1Win')
        self.assertEqual(response.status_code, 201)

        # start and finish all except one the rest of the generated matches
        for x in range(1, expectedMatchCountPerRound - 1):
            response = self._post_to_matches()
            self.assertEqual(response.status_code, 201)
            response = self._post_to_results(response.data['id'], 'Player1Win')
            self.assertEqual(response.status_code, 201)
            # double check the match count
            self.assertEqual(Match.objects.filter(started__isnull=True).count(), expectedMatchCountPerRound - x - 1)

        # at this stage there should be one unstarted match left
        self.assertEqual(Match.objects.filter(started__isnull=True).count(), 1)

        # start the last match
        response2ndRoundLastMatch = self._post_to_matches()
        self.assertEqual(response2ndRoundLastMatch.status_code, 201)
        self.assertEqual(Match.objects.filter(started__isnull=True).count(), 0)

        # the following part ensures round generation is properly handled when an old round in not yet finished
        response = self._post_to_matches()
        self.assertEqual(response.status_code, 201)

        # check match count
        self.assertEqual(Match.objects.filter(started__isnull=True).count(), expectedMatchCountPerRound - 1)
        self.assertEqual(Match.objects.count(), expectedMatchCountPerRound * 3)

        # check round data
        self.assertEqual(Round.objects.count(), 3)

        # check 2nd round data is still the same
        round = Round.objects.get(id=2)
        self.assertIsNotNone(round.started)
        self.assertIsNone(round.finished)
        self.assertFalse(round.complete)

        # check 3rd round data
        round = Round.objects.get(id=3)
        self.assertIsNotNone(round.started)
        self.assertIsNone(round.finished)
        self.assertFalse(round.complete)

        # now finish the 2nd round
        response = self._post_to_results(response2ndRoundLastMatch.data['id'], 'Player1Win')
        self.assertEqual(response.status_code, 201)

        # check round is finished
        round = Round.objects.get(id=2)
        self.assertIsNotNone(round.finished)
        self.assertTrue(round.complete)

        # check 3rd round data remains unmodified
        round = Round.objects.get(id=3)
        self.assertIsNotNone(round.started)
        self.assertIsNone(round.finished)
        self.assertFalse(round.complete)

        # check result count - should have 2 rounds worth of results
        self.assertEqual(Result.objects.count(), expectedMatchCountPerRound * 2)


class SetStatusTestCase(LoggedInMixin, TransactionTestCase):
    def setUp(self):
        super().setUp()
        self.client.force_login(User.objects.get(username='arenaclient1'))

    def test_set_status(self):
        return self.client.post('/api/arenaclient/set-status/',
                                {'status': 'idle'})
