from django.conf import settings
from django.db.models import Sum
from django.test import TransactionTestCase

from aiarena.core.models import Bot, Competition, CompetitionParticipation, MatchParticipation
from aiarena.core.tests.test_mixins import LoggedInMixin


class EloTestCase(LoggedInMixin, TransactionTestCase):
    """
    Tests to ensure ELO calculations run properly.
    """

    def setUp(self):
        super().setUp()

        self.test_client.login(self.staffUser1)

        comp = self._create_game_mode_and_open_competition()
        self._create_map_for_competition("test_map", comp.id)

        self.regularUserBot1 = self._create_bot(self.regularUser1, "regularUserBot1")
        self.regularUserBot2 = self._create_bot(self.regularUser1, "regularUserBot2")

        # self.test_client.login(self.arenaclientUser1)

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
            "Tie",
            "Tie",
            self.regularUserBot2.id,
            "Tie",
            self.regularUserBot2.id,
            self.regularUserBot1.id,
            self.regularUserBot1.id,
            self.regularUserBot1.id,
            self.regularUserBot2.id,
            self.regularUserBot1.id,
            self.regularUserBot1.id,
            "Tie",
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
        response = self._post_to_matches()
        return response.data

    def CreateResult(self, match_id, r_type):
        self._post_to_results(match_id, r_type)

    def DetermineResultType(self, bot1_id, iteration):
        if self.expected_result_sequence[iteration] == "Tie":
            return "Tie"
        else:
            return "Player1Win" if bot1_id == self.expected_result_sequence[iteration] else "Player2Win"

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
        sumElo = CompetitionParticipation.objects.filter(competition=comp).aggregate(Sum("elo"))
        self.assertEqual(
            sumElo["elo__sum"], settings.ELO_START_VALUE * Bot.objects.all().count()
        )  # starting ELO times number of bots

    def test_elo(self):
        for iteration in range(0, self.num_matches_to_play):
            match = self.CreateMatch()
            res = self.DetermineResultType(match["bot1"]["id"], iteration)
            self.CreateResult(match["id"], res)
            self.CheckResultantElos(match["id"], iteration)

        self.CheckFinalElos()

        self.CheckEloSum()

    # an exception won't be raised from this - but a log entry will
    # this is only to ensure no other exception takes place
    def test_elo_sanity_check(self):
        # todo: test log file content
        # log_file = "./logs/aiarena.log"
        # os.remove(log_file)  # clean it

        # intentionally cause a sanity check failure
        self.regularUserBot1.elo = settings.ELO_START_VALUE - 1
        self.regularUserBot1.save()

        match_id = self._post_to_matches().data["id"]
        self._post_to_results(match_id, "Player1Win")

        # with open(log_file, "r") as f:
        #     self.assertFalse("did not match expected value of" in f.read())
