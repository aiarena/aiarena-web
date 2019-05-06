import os

from django.core.files import File
from django.db.models import Sum

from aiarena.arenaclientapi.exceptions import EloSanityCheckException
from aiarena.core.models import *
from aiarena.core.tests import LoggedInTestCase, MatchReadyTestCase


class MatchesTestCase(LoggedInTestCase):

    def test_next_match_not_authorized(self):
        response = self.client.get('/api/matches/next/')
        self.assertEqual(response.status_code, 403)

        self.client.login(username='regular_user', password='x')
        response = self.client.get('/api/matches/next/')
        self.assertEqual(response.status_code, 403)

    def test_next_match(self):
        self.client.login(username='staff_user', password='x')

        # no maps
        response = self.client.get('/api/matches/next/')
        self.assertEqual(response.status_code, 500)

        # not enough active bots
        Map.objects.create(name='testmap')
        response = self.client.get('/api/matches/next/')
        self.assertEqual(response.status_code, 500)

        # not enough active bots
        bot1 = Bot.objects.create(user=self.staffUser, name='testbot1', bot_zip=File(self.test_bot_zip))
        response = self.client.get('/api/matches/next/')
        self.assertEqual(response.status_code, 500)

        # not enough active bots
        bot2 = Bot.objects.create(user=self.regularUser, name='testbot2', bot_zip=File(self.test_bot_zip))
        response = self.client.get('/api/matches/next/')
        self.assertEqual(response.status_code, 500)

        # not enough active bots
        bot1.active = True
        bot1.save()
        response = self.client.get('/api/matches/next/')
        self.assertEqual(response.status_code, 500)

        # success
        bot2.active = True
        bot2.save()
        response = self.client.get('/api/matches/next/')
        self.assertEqual(response.status_code, 200)

        # ensure only 1 match was created
        self.assertEqual(Match.objects.count(), 1)


class ResultsTestCase(LoggedInTestCase):
    def test_create_result_not_authorized(self):
        response = self.client.get('/api/results/')
        self.assertEqual(response.status_code, 403)

        self.client.login(username='regular_user', password='x')
        response = self.client.get('/api/results/')
        self.assertEqual(response.status_code, 403)

    def CreateMatch(self):
        Map.objects.create(name='testmap')

        # For some reason using an absolute file path here for will cause it to mangle the save directory and fail
        # later whilst handling the bot_zip file save
        bot_zip = open('./aiarena/api/test_bot.zip', 'rb')
        bot1 = Bot.objects.create(user=self.regularUser, name='testbot1', bot_zip=File(bot_zip), active=True)
        bot2 = Bot.objects.create(user=self.staffUser, name='testbot2', bot_zip=File(bot_zip), active=True)
        response = self.client.get('/api/matches/next/')
        self.assertEqual(response.status_code, 200)
        return response.data, bot1, bot2

    def PostResult(self, match, winner):
        filename = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'testReplay.SC2Replay')
        with open(filename) as replayFile:
            return self.client.post('/api/results/',
                                    {'match': match["id"],
                                     'winner': winner.id,
                                     'type': 'Player1Win',
                                     'replay_file': replayFile,
                                     'duration': 500})

    def test_create_result(self):
        self.client.login(username='staff_user', password='x')

        match, bot1, bot2 = self.CreateMatch()

        response = self.PostResult(match, bot1)
        self.assertEqual(response.status_code, 201)


class EloTestCase(MatchReadyTestCase):
    """
    Tests to ensure ELO calculations run properly.
    """

    def setUp(self):
        super(EloTestCase, self).setUp()
        self.client.login(username='staff_user', password='x')

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
        response = self.client.get('/api/matches/next/')
        self.assertEqual(response.status_code, 200)

        matchId = response.data['id']

        response = self.client.get('/api/participants/?match={0}&participant_number=1'.format(matchId))
        self.assertEqual(response.status_code, 200)
        participant1 = response.data['results'][0]

        response = self.client.get('/api/participants/?match={0}&participant_number=2'.format(matchId))
        self.assertEqual(response.status_code, 200)
        participant2 = response.data['results'][0]

        return matchId, participant1, participant2

    def CreateResult(self, matchId, winnerId, r_type):
        filename = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'testReplay.SC2Replay')
        with open(filename) as replayFile:
            response = self.client.post('/api/results/',
                                        {'match': matchId,
                                         'winner': winnerId,
                                         'type': r_type,
                                         'replay_file': replayFile,
                                         'duration': 500})
        self.assertEqual(response.status_code, 201, response.data)

    def DetermineResultType(self, p1_bot_id, iteration):
        if self.expected_result_sequence[iteration] == 'Tie':
            return 'Tie'
        else:
            return 'Player1Win' if p1_bot_id == self.expected_result_sequence[iteration] else 'Player2Win'

    def CheckResultantElos(self, match_id, iteration):
        bot1Participant = Participant.objects.filter(match_id=match_id, bot_id=self.regularUserBot1.id)[0]
        bot2Participant = Participant.objects.filter(match_id=match_id, bot_id=self.regularUserBot2.id)[0]

        self.assertEqual(self.expected_resultant_elos[iteration][0], bot1Participant.resultant_elo)
        self.assertEqual(self.expected_resultant_elos[iteration][1], bot2Participant.resultant_elo)

    def CheckFinalElos(self):
        self.regularUserBot1.refresh_from_db()
        self.regularUserBot2.refresh_from_db()
        self.assertEqual(self.regularUserBot1.elo, self.expected_resultant_elos[self.num_matches_to_play-1][0])
        self.assertEqual(self.regularUserBot2.elo, self.expected_resultant_elos[self.num_matches_to_play-1][1])

    def CheckEloSum(self):
        sumElo = Bot.objects.aggregate(Sum('elo'))
        self.assertEqual(sumElo['elo__sum'],
                         ELO_START_VALUE * Bot.objects.all().count())  # starting ELO times number of bots

    def test_elo(self):
        for iteration in range(0, self.num_matches_to_play):
            m_id, p1, p2 = self.CreateMatch()
            res = self.DetermineResultType(p1['bot'], iteration)
            self.CreateResult(m_id, p1['bot'], res)
            self.CheckResultantElos(m_id, iteration)

        self.CheckFinalElos()

        self.CheckEloSum()

    def test_elo_sanity_check(self):
        # intentionally cause a sanity check failure
        self.regularUserBot1.elo = ELO_START_VALUE - 1
        self.regularUserBot1.save()

        m_id, p1, p2 = self.CreateMatch()
        self.assertRaises(EloSanityCheckException, self.CreateResult, m_id, p1['bot'], 'Player1Win')

        self.assertEqual(Result.objects.count(), 0)  # make sure the result was rolled back.
