import os

from constance import config
from django.db.models import Sum
from django.test import TransactionTestCase
from rest_framework.authtoken.models import Token

from aiarena.core.api import Matches
from aiarena.core.models import Match, Bot, MatchParticipation, User, Round, Result, CompetitionParticipation, Competition, Map, \
    ArenaClient, competition_participation
from aiarena.core.models.game_mode import GameMode
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

        self.test_client.login(self.staffUser1)
        self.test_client.set_api_token(Token.objects.get(user=self.arenaclientUser1))

        # no current competition
        response = self._post_to_matches()
        self.assertEqual(response.status_code, 200)

        # needs a valid competition to be able to activate a bot.
        comp = self._create_game_mode_and_open_competition()

        # no maps
        self.test_client.login(self.arenaclientUser1)
        response = self._post_to_matches()
        self.assertEqual(response.status_code, 200)
        self.assertEqual(u'no_current_competitions', response.data['detail'].code)

        # not enough active bots
        self._create_map_for_competition('test_map', comp.id)
        response = self._post_to_matches()
        self.assertEqual(response.status_code, 200)
        self.assertEqual(u'no_current_competitions', response.data['detail'].code)

        # not enough active bots
        bot1 = self._create_bot(self.regularUser1, 'testbot1')
        response = self._post_to_matches()
        self.assertEqual(response.status_code, 200)
        self.assertEqual(u'no_current_competitions', response.data['detail'].code)

        # not enough active bots
        bot2 = self._create_bot(self.regularUser1, 'testbot2')
        response = self._post_to_matches()
        self.assertEqual(response.status_code, 200)
        self.assertEqual(u'no_current_competitions', response.data['detail'].code)

        # not enough active bots
        bot1.competition_participations.create(competition=comp)
        response = self._post_to_matches()
        self.assertEqual(response.status_code, 200)
        self.assertEqual(u'no_current_competitions', response.data['detail'].code)

        # success
        bot2.competition_participations.create(competition=comp)
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

        self.test_client.login(self.staffUser1)
        comp = self._create_game_mode_and_open_competition()
        self._create_map_for_competition('test_map', comp.id)

        self._create_active_bot_for_competition(comp.id, self.regularUser1, 'testbot1', 'T')
        self._create_active_bot_for_competition(comp.id, self.regularUser1, 'testbot2', 'Z')

        self.test_client.login(self.arenaclientUser1)
        response_m1 = self.client.post('/api/arenaclient/matches/')
        self.assertEqual(response_m1.status_code, 201)

        # should be the same match reissued
        response_m2 = self.client.post('/api/arenaclient/matches/')
        self.assertEqual(response_m2.status_code, 201)

        self.assertEqual(response_m1.data['id'], response_m2.data['id'])

    def test_match_requests_no_open_competition(self):
        """
        Tests that match requests still run when no competitions are open.
        :return:
        """

        self.test_client.login(self.staffUser1)
        game = self.test_client.create_game("StarCraft II")
        game_mode = self.test_client.create_gamemode('Melee', game.id)
        Map.objects.create(name="testmap", game_mode=game_mode)

        bot1 = self._create_bot(self.regularUser1, 'testbot1', 'T')
        bot2 = self._create_bot(self.regularUser1, 'testbot2', 'Z')

        self.test_client.login(self.arenaclientUser1)

        # we shouldn't be able to get a new match
        response = self.client.post('/api/arenaclient/matches/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(u"no_current_competitions", response.data['detail'].code)

        Matches.request_match(self.regularUser2, bot1, bot1.get_random_excluding_self(),
                              game_mode=game_mode)

        # now we should be able to get a match - the requested one
        response = self.client.post('/api/arenaclient/matches/')
        self.assertEqual(response.status_code, 201)


    def test_max_active_rounds(self):
        # we don't want to have to create lots of arenaclients for multiple matches
        config.REISSUE_UNFINISHED_MATCHES = False

        self.test_client.login(self.staffUser1)

        # competitions will default to max 2 active rounds
        comp = self._create_game_mode_and_open_competition()
        self._create_map_for_competition('test_map', comp.id)

        bot1 = self._create_active_bot_for_competition(comp.id, self.regularUser1, 'testbot1', 'T')
        bot2 = self._create_active_bot_for_competition(comp.id, self.regularUser1, 'testbot2', 'Z')
        bot3 = self._create_active_bot_for_competition(comp.id, self.regularUser1, 'testbot3', 'P')
        bot4 = self._create_active_bot_for_competition(comp.id, self.regularUser1, 'testbot4', 'R')

        # Round 1
        self.test_client.login(self.arenaclientUser1)
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

        self.test_client.login(self.staffUser1)
        comp = self._create_game_mode_and_open_competition()
        self._create_map_for_competition('test_map', comp.id)

        bot1 = self._create_active_bot_for_competition(comp.id,  self.regularUser1, 'testbot1', 'T')
        bot2 = self._create_active_bot_for_competition(comp.id, self.regularUser1, 'testbot2', 'Z')

        self.test_client.login(self.arenaclientUser1)
        # this should tie up both bots
        response = self.client.post('/api/arenaclient/matches/')
        self.assertEqual(response.status_code, 201)

        # we shouldn't be able to get a new match
        self.test_client.login(self.arenaclientUser2)
        response = self.client.post('/api/arenaclient/matches/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(u"Not enough available bots for a match. Wait until more bots become available.", response.data['detail'])

        Matches.request_match(self.regularUser2, bot1, bot1.get_random_active_excluding_self(),
                              game_mode=GameMode.objects.first())

        # now we should be able to get a match - the requested one
        response = self.client.post('/api/arenaclient/matches/')
        self.assertEqual(response.status_code, 201)



class ResultsTestCase(LoggedInMixin, TransactionTestCase):
    uploaded_bot_data_path = os.path.join(BASE_DIR, PRIVATE_STORAGE_ROOT, 'bots', '{0}', 'bot_data')
    uploaded_bot_data_backup_path = os.path.join(BASE_DIR, PRIVATE_STORAGE_ROOT, 'bots', '{0}', 'bot_data_backup')
    uploaded_match_log_path = os.path.join(BASE_DIR, PRIVATE_STORAGE_ROOT, 'match-logs', '{0}')
    uploaded_arenaclient_log_path = os.path.join(MEDIA_ROOT, 'arenaclient-logs', '{0}_arenaclientlog.zip')

    def test_create_results(self):
        self.test_client.login(self.staffUser1)
        self.test_client.set_api_token(Token.objects.get(user=self.arenaclientUser1))

        comp = self._create_game_mode_and_open_competition()
        self._create_map_for_competition('test_map', comp.id)

        bot1 = self._create_active_bot_for_competition(comp.id, self.regularUser1, 'bot1')
        bot2 = self._create_active_bot_for_competition(comp.id, self.regularUser1, 'bot2', 'Z')

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
        match5 = Matches.request_match(self.staffUser1, bot1, bot2, game_mode=GameMode.objects.get(id=1))
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
        self.test_client.login(self.staffUser1)
        self.test_client.set_api_token(Token.objects.get(user=self.arenaclientUser1))

        comp = self._create_game_mode_and_open_competition()
        self._create_map_for_competition('test_map', comp.id)

        # Create 3 bots, so after a round is generated, we'll have some unstarted matches
        bot1 = self._create_active_bot_for_competition(comp.id, self.regularUser1, 'bot1')
        bot2 = self._create_active_bot_for_competition(comp.id, self.regularUser1, 'bot2', 'Z')
        bot3 = self._create_active_bot_for_competition(comp.id, self.regularUser1, 'bot3', 'P')
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

        self.test_client.login(self.staffUser1)

        comp = self._create_game_mode_and_open_competition()
        self._create_map_for_competition('test_map', comp.id)

        bot1 = self._create_active_bot_for_competition(comp.id, self.regularUser1, 'bot1')
        bot2 = self._create_active_bot_for_competition(comp.id, self.regularUser1, 'bot2', 'Z')

        self.test_client.set_api_token(Token.objects.get(user=self.arenaclientUser1))

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
        for cp in bot1.competition_participations.all():
            self.assertFalse(cp.active)

        # not enough active bots
        response = self._post_to_matches()
        self.assertEqual(response.status_code, 200)
        self.assertEqual(u'no_current_competitions', response.data['detail'].code)

        # Post a successful match, then retry the crashes to make sure the previous ones don't affect the check
        cp = bot1.competition_participations.first()
        cp.active = True
        cp.save()
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
        for cp in bot1.competition_participations.all():
            self.assertFalse(cp.active)

        # not enough active bots
        response = self._post_to_matches()
        self.assertEqual(response.status_code, 200)
        self.assertEqual(u'no_current_competitions', response.data['detail'].code)


class EloTestCase(LoggedInMixin, TransactionTestCase):
    """
    Tests to ensure ELO calculations run properly.
    """

    def setUp(self):
        super(EloTestCase, self).setUp()

        self.test_client.login(self.staffUser1)

        self.regularUserBot1 = self._create_bot(self.regularUser1, 'regularUserBot1')
        self.regularUserBot2 = self._create_bot(self.regularUser1, 'regularUserBot2')
        comp = self._create_game_mode_and_open_competition()
        self._create_map_for_competition('test_map', comp.id)

        self.test_client.login(self.arenaclientUser1)

        # activate the required bots
        self.regularUserBot1.competition_participations.create(competition=comp)
        self.regularUserBot2.competition_participations.create(competition=comp)

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
        cp1 = self.regularUserBot1.competition_participations.get()
        cp2 = self.regularUserBot2.competition_participations.get()
        self.assertEqual(cp1.elo, self.expected_resultant_elos[self.num_matches_to_play - 1][0])
        self.assertEqual(cp2.elo, self.expected_resultant_elos[self.num_matches_to_play - 1][1])

    def CheckEloSum(self):
        comp = Competition.objects.get()
        sumElo = CompetitionParticipation.objects.filter(competition=comp).aggregate(Sum('elo'))
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
        super().setUp()
        self.client.force_login(User.objects.get(username='arenaclient1'))

    def test_round_robin_generation(self):
        # avoid old tests breaking that were pre-this feature
        config.REISSUE_UNFINISHED_MATCHES = False

        # freeze every comp but one, so we can get anticipatable results
        active_comp = Competition.objects.filter(status='open').first()
        Competition.objects.exclude(id=active_comp.id).update(status='frozen')

        botCount = CompetitionParticipation.objects.filter(active=True, competition=active_comp).count()
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


class CompetitionsDivisionsTestCase(MatchReadyMixin, TransactionTestCase):
    """
    Test competition divisions
    """


    def setUp(self):
        super().setUp()
        self._generate_extra_users()
        self._generate_extra_bots()
        self.client.force_login(User.objects.get(username='arenaclient1'))

    def test_split_merge_logic(self):
        def _check(competition, n_bots, split_points, merge_points):
            # Add bots to competition
            for i in range(n_bots):
                if i in split_points:
                    self.assertEqual(competition.should_split_divisions(i), True)
                    competition.n_divisions += 1
                else:
                    self.assertEqual(competition.should_split_divisions(i), False)
            # Remove bots from competition
            competition.n_divisions = competition.target_n_divisions
            for i in range(n_bots, 0, -1):
                if i in merge_points:
                    self.assertEqual(competition.should_merge_divisions(i), True)
                    competition.n_divisions -= 1
                else:
                    self.assertEqual(competition.should_merge_divisions(i), False)

        competition = self._create_open_competition(GameMode.objects.first().id, 'Split/Merge Test Competition')
        # By default there should be no splitting happening
        _check(competition, 50, [], [])
        # 2 divisions      
        competition.target_n_divisions = 2
        competition.n_divisions = 1
        competition.target_division_size = 15
        _check(competition, 100, [30], [22])
        # 3 divisions
        competition.target_n_divisions = 3
        competition.n_divisions = 1
        competition.target_division_size = 8
        _check(competition, 50, [16, 24], [12, 20])
        # small divisions
        competition.target_n_divisions = 5
        competition.n_divisions = 1
        competition.target_division_size = 2
        _check(competition, 20, [4, 6, 8, 10], [3, 5, 7, 9])
        # small divisions
        competition.target_n_divisions = 4
        competition.n_divisions = 1
        competition.target_division_size = 3
        _check(competition, 30, [6, 9, 12], [4, 7, 10])

    def _get_div_participant_count(self, competition):
        div_participants = dict()
        current_elo = -1
        current_div = competition.target_n_divisions
        current_match_count = -1
        current_in_placements = True
        existing_participants = CompetitionParticipation.objects.filter(active=True, competition=competition, in_placements=False).only('division_num','elo','match_count','in_placements').order_by('-division_num','elo')
        placement_participants = CompetitionParticipation.objects.filter(active=True, competition=competition, in_placements=True).only('division_num','elo','match_count','in_placements').order_by('-division_num','match_count','elo')
        for cp in list(placement_participants) + list(existing_participants):
            if cp.in_placements:
                self.assertEqual(current_in_placements, True) # Preceding bot should be in placement
                self.assertGreaterEqual(cp.match_count, current_match_count) # Asc match count
                if competition.n_placements > 0 and competition.rounds_this_cycle==1:
                    self.assertLess(cp.match_count, competition.n_placements) # Should have less matches played than placement reqs
            else:
                if not current_in_placements and competition.rounds_this_cycle==1:
                    self.assertGreaterEqual(cp.elo, current_elo) # Asc ELO
                self.assertGreaterEqual(cp.match_count, competition.n_placements) # Should have at least equal matches played than placement reqs
            self.assertLessEqual(cp.division_num, current_div) # Desc Div nums
            current_match_count = cp.match_count
            current_in_placements = cp.in_placements
            current_elo = cp.elo
            current_div = cp.division_num
            if cp.division_num in div_participants:
                div_participants[cp.division_num]['n'] += 1
                div_participants[cp.division_num]['p'] += 1 if cp.in_placements else 0
            else:
                div_participants[cp.division_num] = { 'n':1, 'p':1 if cp.in_placements else 0}
        return div_participants

    def _get_expected_matches_per_div(self, round):
        matches_per_div = dict()
        for m in Match.objects.filter(round=round):
            div = m.participant1.competition_participant.division_num
            self.assertEqual(div, m.participant2.competition_participant.division_num)
            if div in matches_per_div:
                matches_per_div[div] += 1
            else:
                matches_per_div[div] = 1
        return matches_per_div

    def _complete_round(self, competition, exp_round, exp_div_participant_count, exp_n_matches):
        # this should trigger a new round
        response = self._post_to_matches()  
        self.assertEqual(response.status_code, 201)
        # check round data
        round = Round.objects.filter(competition=competition).order_by('-number').first()
        self.assertEqual(round.number, exp_round)
        self.assertIsNotNone(round.started)
        self.assertIsNone(round.finished)
        self.assertFalse(round.complete)
        # check match count, also checks divisions are in elo order
        competition.refresh_from_db()
        self.assertEqual(self._get_div_participant_count(competition), exp_div_participant_count)
        exp_matches_per_div = self._get_expected_matches_per_div(round)
        self.assertEqual(exp_matches_per_div, exp_n_matches)
        total_exp_matches_per_div = sum(exp_matches_per_div.values())
        self.assertEqual(Match.objects.filter(round=round).count(), total_exp_matches_per_div)
        # finish the initial match
        response = self._post_to_results(response.data['id'], 'Player1Win')
        self.assertEqual(response.status_code, 201)

        # start and finish all the rest of the generated matches
        for x in range(1, total_exp_matches_per_div):
            response = self._post_to_matches()
            self.assertEqual(response.status_code, 201)
            response = self._post_to_results(response.data['id'], 'Player1Win')
            self.assertEqual(response.status_code, 201)
            # double check the match count
            self.assertEqual(Match.objects.filter(started__isnull=True).count(), total_exp_matches_per_div - x - 1)

        # check round is finished
        round = Round.objects.filter(competition=competition).order_by('-number').first()
        self.assertEqual(round.number, exp_round)
        self.assertIsNotNone(round.finished)
        self.assertTrue(round.complete)

    def _complete_cycle(self, competition, exp_rounds, exp_div_participant_count, exp_n_matches):
        for i in range(competition.rounds_per_cycle):
            self._complete_round(competition, exp_rounds[i], exp_div_participant_count, exp_n_matches)
            self.assertEqual(competition.rounds_this_cycle, i+1)

    def _set_up_competition(self, target_divs, div_size, rpc=1, n_placements=0): 
        # avoid old tests breaking that were pre-this feature
        config.REISSUE_UNFINISHED_MATCHES = False

        # freeze every comp but one, so we can get anticipatable results
        competition = self._create_open_competition(GameMode.objects.first().id, 'Test Competition')
        # Set up division settings
        competition.target_n_divisions = target_divs
        competition.target_division_size = div_size
        competition.n_placements = n_placements
        competition.rounds_per_cycle = rpc
        competition.save()
        Competition.objects.exclude(id=competition.id).update(status='frozen')
        self._create_map_for_competition('testmapdiv1', competition.id)
        self.assertEqual(Match.objects.count(), 0)  # starting with 0 matches
        self.assertEqual(Round.objects.count(), 0)  # starting with 0 rounds
        return competition

    def test_placements_enabled(self):
        competition = self._set_up_competition(3, 3, 2, 6)
        _exp_par = lambda x, y: {'n':x,'p':y}
        CompetitionParticipation.objects.create(bot_id=self.regularUser1Bot1.id, competition_id=competition.id)
        CompetitionParticipation.objects.create(bot_id=self.staffUser1Bot1.id, competition_id=competition.id)
        self._complete_cycle(competition, [1,2], {0:_exp_par(2,2)}, {0:1})
        CompetitionParticipation.objects.create(bot_id=self.regularUser1Bot2.id, competition_id=competition.id)
        self._complete_cycle(competition, [3,4], {0:_exp_par(3,3)}, {0:3})
        self._complete_cycle(competition, [5,6], {0:_exp_par(3,1)}, {0:3})
        CompetitionParticipation.objects.create(bot_id=self.staffUser1Bot2.id, competition_id=competition.id)
        CompetitionParticipation.objects.create(bot_id=self.regularUser1Bot3.id, competition_id=competition.id)
        CompetitionParticipation.objects.create(bot_id=self.staffUser1Bot3.id, competition_id=competition.id)
        CompetitionParticipation.objects.create(bot_id=self.regularUser1Bot4.id, competition_id=competition.id)
        CompetitionParticipation.objects.create(bot_id=self.regularUser2Bot1.id, competition_id=competition.id)
        CompetitionParticipation.objects.create(bot_id=self.regularUser2Bot2.id, competition_id=competition.id)
        CompetitionParticipation.objects.create(bot_id=self.regularUser3Bot1.id, competition_id=competition.id)
        CompetitionParticipation.objects.create(bot_id=self.regularUser3Bot2.id, competition_id=competition.id)
        CompetitionParticipation.objects.create(bot_id=self.regularUser4Bot1.id, competition_id=competition.id)
        CompetitionParticipation.objects.create(bot_id=self.regularUser4Bot2.id, competition_id=competition.id)
        for j in range(3):
            u = User.objects.create_user(username=f'regular_user{100+j}', password='x', email=f'regular_user{100+j}@dev.aiarena.net')
            for i in range(3):
                self._create_active_bot_for_competition(competition.id, u, f'{u.username}Bot{i+1}')
        self._complete_cycle(competition, [7,8], {0:_exp_par(7,4), 1:_exp_par(7,7), 2:_exp_par(8,8)}, {0:21, 1:21, 2:28})
        self._complete_cycle(competition, [9,10], {0:_exp_par(7,0), 1:_exp_par(7,0), 2:_exp_par(8,0)}, {0:21, 1:21, 2:28})

    
    def test_division_matchmaking(self):
        competition = self._set_up_competition(3, 3, 3)

        _exp_par = lambda x: {'n':x,'p':0}
        # Start Rounds
        CompetitionParticipation.objects.create(bot_id=self.regularUser1Bot1.id, competition_id=competition.id)
        CompetitionParticipation.objects.create(bot_id=self.staffUser1Bot1.id, competition_id=competition.id)
        self._complete_cycle(competition, [1,2,3], {0:_exp_par(2)}, {0:1})
        CompetitionParticipation.objects.create(bot_id=self.regularUser1Bot2.id, competition_id=competition.id)
        CompetitionParticipation.objects.create(bot_id=self.staffUser1Bot2.id, competition_id=competition.id)
        self._complete_cycle(competition, [4,5,6], {0:_exp_par(4)}, {0:6})
        # Split to 2 divs
        self.ru1b3_cp = CompetitionParticipation.objects.create(bot_id=self.regularUser1Bot3.id, competition_id=competition.id)
        self.su1b3_cp = CompetitionParticipation.objects.create(bot_id=self.staffUser1Bot3.id, competition_id=competition.id)
        self._complete_cycle(competition, [7,8,9], {0:_exp_par(3), 1:_exp_par(3)}, {0:3, 1:3})
        # Bot inactive dont merge yet
        self.ru1b3_cp.active = False
        self.ru1b3_cp.save()
        self._complete_cycle(competition, [10,11,12], {0:_exp_par(2), 1:_exp_par(3)}, {0:1, 1:3})
        # Merge threshold reached
        self.su1b3_cp.active = False
        self.su1b3_cp.save()
        self._complete_cycle(competition, [13,14,15], {0:_exp_par(4)}, {0:6})
        # Non equal divisions
        self.ru1b3_cp.active = True
        self.ru1b3_cp.save()
        self.su1b3_cp.active = True
        self.su1b3_cp.save()
        self.ru1b4_cp = CompetitionParticipation.objects.create(bot_id=self.regularUser1Bot4.id, competition_id=competition.id)
        self._complete_cycle(competition, [16,17,18], {0:_exp_par(3), 1:_exp_par(4)}, {0:3, 1:6})
        # Split to 3 divs
        self.ru2b1_cp = CompetitionParticipation.objects.create(bot_id=self.regularUser2Bot1.id, competition_id=competition.id)
        self.ru2b2_cp = CompetitionParticipation.objects.create(bot_id=self.regularUser2Bot2.id, competition_id=competition.id)
        self._complete_cycle(competition, [19,20,21], {0:_exp_par(3), 1:_exp_par(3), 2:_exp_par(3)}, {0:3, 1:3, 2:3})
        # Merge again
        self.ru1b3_cp.active = False
        self.ru1b3_cp.save()
        self._complete_cycle(competition, [22,23,24], {0:_exp_par(2), 1:_exp_par(3), 2:_exp_par(3)}, {0:1, 1:3, 2:3})
        self.su1b3_cp.active = False
        self.su1b3_cp.save()
        self._complete_cycle(competition, [25,26,27], {0:_exp_par(3), 1:_exp_par(4)}, {0:3, 1:6})
        self.ru2b1_cp.active = False
        self.ru2b1_cp.save()
        self._complete_cycle(competition, [28,29,30],{0:_exp_par(3), 1:_exp_par(3)}, {0:3, 1:3})
        self.ru1b3_cp.active = True
        self.ru1b3_cp.save()
        self.su1b3_cp.active = True
        self.su1b3_cp.save()
        self.ru2b1_cp.active = True
        self.ru2b1_cp.save()
        self._complete_cycle(competition, [31,32,33], {0:_exp_par(3), 1:_exp_par(3), 2:_exp_par(3)}, {0:3, 1:3, 2:3})
        # Grow equally
        CompetitionParticipation.objects.create(bot_id=self.regularUser3Bot1.id, competition_id=competition.id)
        CompetitionParticipation.objects.create(bot_id=self.regularUser3Bot2.id, competition_id=competition.id)
        CompetitionParticipation.objects.create(bot_id=self.regularUser4Bot1.id, competition_id=competition.id)
        CompetitionParticipation.objects.create(bot_id=self.regularUser4Bot2.id, competition_id=competition.id)
        self._complete_cycle(competition, [34,35,36], {0:_exp_par(4), 1:_exp_par(4), 2:_exp_par(5)}, {0:6, 1:6, 2:10})
        self._create_active_bot_for_competition(competition.id, self.regularUser2, 'regularUser2Bot100')
        self._complete_cycle(competition, [37,38,39], {0:_exp_par(4), 1:_exp_par(5), 2:_exp_par(5)}, {0:6, 1:10, 2:10})
        # Not more splits
        for j in range(3):
            u = User.objects.create_user(username=f'regular_user{100+j}', password='x', email=f'regular_user{100+j}@dev.aiarena.net')
            for i in range(3):
                self._create_active_bot_for_competition(competition.id, u, f'{u.username}Bot{i+1}')
        self._complete_cycle(competition, [40,41,42], {0:_exp_par(7), 1:_exp_par(8), 2:_exp_par(8)}, {0:21, 1:28, 2:28})

        
class SetStatusTestCase(LoggedInMixin, TransactionTestCase):
    def setUp(self):
        super().setUp()
        self.client.force_login(User.objects.get(username='arenaclient1'))

    def test_set_status(self):
        return self.client.post('/api/arenaclient/set-status/',
                                {'status': 'idle'})
