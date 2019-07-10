import os
from datetime import timedelta

from django.db.models import Sum
from django.utils import timezone

from aiarena.core.models import Match, Bot, Participant, User, Round, Result
from aiarena.core.tests import LoggedInTestCase, MatchReadyTestCase
from aiarena.core.utils import calculate_md5
from aiarena.settings import ELO_START_VALUE, BASE_DIR, PRIVATE_STORAGE_ROOT


class MatchesTestCase(LoggedInTestCase):
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
        self.client.login(username='staff_user', password='x')

        # no maps
        response = self._post_to_matches()
        self.assertEqual(response.status_code, 409)

        # not enough active bots
        self._create_map('test_map')
        response = self._post_to_matches()
        self.assertEqual(response.status_code, 409)

        # not enough active bots
        bot1 = self._create_bot(self.regularUser1, 'testbot1')
        response = self._post_to_matches()
        self.assertEqual(response.status_code, 409)

        # not enough active bots
        bot2 = self._create_bot(self.regularUser1, 'testbot2')
        response = self._post_to_matches()
        self.assertEqual(response.status_code, 409)

        # not enough active bots
        bot1.active = True
        bot1.save()
        response = self._post_to_matches()
        self.assertEqual(response.status_code, 409)

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
        self.assertEqual(response.status_code, 409)

        # ensure only 1 match was created
        self.assertEqual(Match.objects.count(), 1)

    def test_previous_match_timeout(self):
        self.client.login(username='staff_user', password='x')
        self._create_map('test_map')
        bot1 = self._create_active_bot(self.regularUser1, 'testbot1', 'T')
        bot2 = self._create_active_bot(self.regularUser1, 'testbot2', 'Z')
        bot3 = self._create_active_bot(self.regularUser1, 'testbot3', 'P')
        bot4 = self._create_active_bot(self.regularUser1, 'testbot4', 'R')
        bot5 = self._create_active_bot(self.regularUser2, 'testbot5', 'T')
        bot6 = self._create_active_bot(self.regularUser2, 'testbot6', 'Z')
        bot7 = self._create_active_bot(self.regularUser2, 'testbot7', 'P')
        bot8 = self._create_active_bot(self.regularUser2, 'testbot8', 'R')

        response = self.client.post('/api/arenaclient/matches/')
        self.assertEqual(response.status_code, 201)

        # save the match for modification
        match1 = Match.objects.get(id=response.data['id'])

        # generate a new match so we can check it isn't interfered with
        response = self.client.post('/api/arenaclient/matches/')
        self.assertEqual(response.status_code, 201)
        match2 = Match.objects.get(id=response.data['id'])

        # set the created time back into the past long enough for it to cause a time out
        match1.started = timezone.now() - timedelta(hours=2)
        match1.save()

        response = self.client.post('/api/arenaclient/matches/')
        self.assertEqual(response.status_code, 201)

        # confirm these bots were successfully force removed from their match
        self.assertEqual(match1.bots_currently_in_match.count(), 0)
        for bot in match1.bots_currently_in_match.all():
            self.assertFalse(bot.in_match)
            self.assertTrue(bot.current_match is None)

        # confirm these bots weren't affected
        self.assertEqual(match2.bots_currently_in_match.count(), 2)
        for bot in match2.bots_currently_in_match.all():
            self.assertTrue(bot.in_match)
            self.assertTrue(bot.current_match is not None)

        # final count double checks
        self.assertEqual(Bot.objects.filter(in_match=False, current_match=None).count(), 4)
        self.assertEqual(Bot.objects.filter(in_match=True).exclude(current_match=None).count(), 4)


class ResultsTestCase(LoggedInTestCase):
    uploaded_bot_data_path = os.path.join(BASE_DIR, PRIVATE_STORAGE_ROOT, 'bots/{0}/bot_data')
    uploaded_bot_data_backup_path = os.path.join(BASE_DIR, PRIVATE_STORAGE_ROOT, 'bots/{0}/bot_data_backup')

    def test_create_results(self):
        self.client.login(username='staff_user', password='x')

        bot1 = self._create_active_bot(self.regularUser1, 'bot1')
        bot2 = self._create_active_bot(self.regularUser1, 'bot2', 'Z')
        self._create_map('test_map')

        # post a standard result
        match = self._post_to_matches().data
        response = self._post_to_results(match['id'], 'Player1Win')
        self.assertEqual(response.status_code, 201)

        # check bot datas exist
        self.assertTrue(os.path.exists(self.uploaded_bot_data_path.format(bot1.id)))
        self.assertTrue(os.path.exists(self.uploaded_bot_data_path.format(bot2.id)))
        # check hashes
        self.assertEqual('85c200fd57f605a3a333302e5df2bc24', Bot.objects.get(id=bot1.id).bot_data_md5hash)
        self.assertEqual('85c200fd57f605a3a333302e5df2bc24', Bot.objects.get(id=bot2.id).bot_data_md5hash)

        # post a standard result
        match = self._post_to_matches().data
        response = self._post_to_results(match['id'], 'Player1Win')
        self.assertEqual(response.status_code, 201)

        # check bot datas and their backups exist
        self.assertTrue(os.path.exists(self.uploaded_bot_data_path.format(bot1.id)))
        self.assertTrue(os.path.exists(self.uploaded_bot_data_path.format(bot2.id)))
        self.assertTrue(os.path.exists(self.uploaded_bot_data_backup_path.format(bot1.id)))
        self.assertTrue(os.path.exists(self.uploaded_bot_data_backup_path.format(bot2.id)))
        # todo: change bot_data content so hashes are alterred
        # check hashes - nothing should have changed
        self.assertEqual('85c200fd57f605a3a333302e5df2bc24', Bot.objects.get(id=bot1.id).bot_data_md5hash)
        self.assertEqual('85c200fd57f605a3a333302e5df2bc24', Bot.objects.get(id=bot2.id).bot_data_md5hash)

        # post a standard result with no bot1 data
        match = self._post_to_matches().data
        response = self._post_to_results_no_bot1_data(match['id'], 'Player1Win')
        self.assertEqual(response.status_code, 201)

        # check hashes - nothing should have changed
        self.assertEqual('85c200fd57f605a3a333302e5df2bc24', Bot.objects.get(id=bot1.id).bot_data_md5hash)
        self.assertEqual('85c200fd57f605a3a333302e5df2bc24', Bot.objects.get(id=bot2.id).bot_data_md5hash)

        # post a standard result with no bot2 data
        match = self._post_to_matches().data
        response = self._post_to_results_no_bot2_data(match['id'], 'Player1Win')
        self.assertEqual(response.status_code, 201)

        # check hashes - nothing should have changed
        self.assertEqual('85c200fd57f605a3a333302e5df2bc24', Bot.objects.get(id=bot1.id).bot_data_md5hash)
        self.assertEqual('85c200fd57f605a3a333302e5df2bc24', Bot.objects.get(id=bot2.id).bot_data_md5hash)

        # post a win without a replay - now allowed due to corrupt replays being omitted
        # match = self._post_to_matches().data
        # response = self._post_to_results_no_replay(match['id'], 'Player2Win')
        # self.assertEqual(response.status_code, 400)
        # self.assertTrue('non_field_errors' in response.data)
        # self.assertEqual(response.data['non_field_errors'][0], 'A win/loss or tie result must contain a replay file.')

        # check hashes - nothing should have changed
        self.assertEqual('85c200fd57f605a3a333302e5df2bc24', Bot.objects.get(id=bot1.id).bot_data_md5hash)
        self.assertEqual('85c200fd57f605a3a333302e5df2bc24', Bot.objects.get(id=bot2.id).bot_data_md5hash)

    def test_create_result_bot_not_in_match(self):
        self.client.login(username='staff_user', password='x')

        bot1 = self._create_active_bot(self.regularUser1, 'bot1')
        bot2 = self._create_active_bot(self.regularUser1, 'bot2', 'Z')
        self._create_map('test_map')
        response = self._post_to_matches()
        self.assertEqual(response.status_code, 201)
        match = response.data

        bot1.in_match = False  # force the exception
        bot1.save()

        response = self._post_to_results(match['id'], 'Player1Win')
        self.assertEqual(response.status_code, 500)
        self.assertTrue('detail' in response.data)
        self.assertEqual(u'Unable to log result - one of the bots is not listed as in this match.',
                         response.data['detail'])

        bot2.in_match = False  # check bot 2 as well
        bot2.save()
        bot1.in_match = True
        bot1.save()

        response = self._post_to_results(match['id'], 'Player1Win')
        self.assertEqual(response.status_code, 500)
        self.assertTrue('detail' in response.data)
        self.assertEqual(u'Unable to log result - one of the bots is not listed as in this match.',
                         response.data['detail'])

    def test_get_results_not_authorized(self):
        response = self.client.get('/api/arenaclient/results/')
        self.assertEqual(response.status_code, 403)

        self.client.login(username='regular_user', password='x')
        response = self.client.get('/api/arenaclient/results/')
        self.assertEqual(response.status_code, 403)


class EloTestCase(LoggedInTestCase):
    """
    Tests to ensure ELO calculations run properly.
    """

    def setUp(self):
        super(EloTestCase, self).setUp()
        self.client.login(username='staff_user', password='x')

        self.regularUserBot1 = self._create_bot(self.regularUser1, 'regularUserBot1')
        self.regularUserBot2 = self._create_bot(self.regularUser1, 'regularUserBot2')
        self._create_map('testmap')

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
            [1608, 1592],
            [1600, 1600],
            [1608, 1592],
            [1616, 1584],
            [1623, 1577],
            [1622, 1578],
            [1621, 1579],
            [1612, 1588],
            [1611, 1589],
            [1602, 1598],
            [1610, 1590],
            [1618, 1582],
            [1625, 1575],
            [1616, 1584],
            [1623, 1577],
            [1630, 1570],
            [1629, 1571],
            [1636, 1564],
            [1642, 1558],
            [1648, 1552],
        ]

    def CreateMatch(self):
        response = self.client.post('/api/arenaclient/matches/')
        self.assertEqual(response.status_code, 201)
        return response.data

    def CreateResult(self, match_id, winner_id, r_type):
        filename = os.path.join(os.path.dirname(os.path.realpath(__file__)), '../../core/testReplay.SC2Replay')
        with open(filename) as replayFile:
            response = self.client.post('/api/arenaclient/results/',
                                        {'match': match_id,
                                         'winner': winner_id,
                                         'type': r_type,
                                         'replay_file': replayFile,
                                         'duration': 500})
        self.assertEqual(response.status_code, 201, response.data)

    def DetermineResultType(self, bot1_id, iteration):
        if self.expected_result_sequence[iteration] == 'Tie':
            return 'Tie'
        else:
            return 'Player1Win' if bot1_id == self.expected_result_sequence[iteration] else 'Player2Win'

    def CheckResultantElos(self, match_id, iteration):
        bot1_participant = Participant.objects.filter(match_id=match_id, bot_id=self.regularUserBot1.id)[0]
        bot2_participant = Participant.objects.filter(match_id=match_id, bot_id=self.regularUserBot2.id)[0]

        self.assertEqual(self.expected_resultant_elos[iteration][0], bot1_participant.resultant_elo)
        self.assertEqual(self.expected_resultant_elos[iteration][1], bot2_participant.resultant_elo)

    def CheckFinalElos(self):
        self.regularUserBot1.refresh_from_db()
        self.regularUserBot2.refresh_from_db()
        self.assertEqual(self.regularUserBot1.elo, self.expected_resultant_elos[self.num_matches_to_play - 1][0])
        self.assertEqual(self.regularUserBot2.elo, self.expected_resultant_elos[self.num_matches_to_play - 1][1])

    def CheckEloSum(self):
        sumElo = Bot.objects.aggregate(Sum('elo'))
        self.assertEqual(sumElo['elo__sum'],
                         ELO_START_VALUE * Bot.objects.all().count())  # starting ELO times number of bots

    def test_elo(self):
        for iteration in range(0, self.num_matches_to_play):
            match = self.CreateMatch()
            res = self.DetermineResultType(match['bot1']['id'], iteration)
            self.CreateResult(match['id'], match['bot1']['id'], res)
            self.CheckResultantElos(match['id'], iteration)

        self.CheckFinalElos()

        self.CheckEloSum()

    # an exception won't be raised from this - but a log entry will
    # this is only to ensure no other exception takes place
    def test_elo_sanity_check(self):
        # intentionally cause a sanity check failure
        self.regularUserBot1.elo = ELO_START_VALUE - 1
        self.regularUserBot1.save()

        match = self._post_to_matches().data
        self._post_to_results(match['id'], 'Player1Win')


class RoundRobinGenerationTestCase(MatchReadyTestCase):
    def setUp(self):
        super(RoundRobinGenerationTestCase, self).setUp()
        self.client.login(username='staff_user', password='x')

    def test_round_robin_generation(self):  # todo: test for round generation and completion
        botCount = Bot.objects.filter(active=True).count()
        expectedMatchCountPerRound = int(botCount/2*(botCount-1))
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
            self.assertEqual(Match.objects.filter(started__isnull=True).count(), expectedMatchCountPerRound-x-1)

        # check round is finished
        self.assertEqual(Round.objects.count(), 1)
        round = Round.objects.get(id=1)
        self.assertIsNotNone(round.finished)
        self.assertTrue(round.complete)

        # Repeat again but with quirks

        response = self._post_to_matches()  # this should trigger another new round robin generation
        self.assertEqual(response.status_code, 201)

        # check match count
        self.assertEqual(Match.objects.count(), expectedMatchCountPerRound*2)

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
        for x in range(1, expectedMatchCountPerRound-1):
            response = self._post_to_matches()
            self.assertEqual(response.status_code, 201)
            response = self._post_to_results(response.data['id'], 'Player1Win')
            self.assertEqual(response.status_code, 201)
            # double check the match count
            self.assertEqual(Match.objects.filter(started__isnull=True).count(), expectedMatchCountPerRound-x-1)

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
        self.assertEqual(Match.objects.filter(started__isnull=True).count(), expectedMatchCountPerRound-1)
        self.assertEqual(Match.objects.count(), expectedMatchCountPerRound*3)

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
        self.assertEqual(Result.objects.count(), expectedMatchCountPerRound*2)

