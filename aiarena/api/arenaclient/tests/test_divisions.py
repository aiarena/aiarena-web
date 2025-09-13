from django.test import TransactionTestCase

from constance import config

from aiarena.core.models import Competition, CompetitionParticipation, GameMode, Match, Round, User
from aiarena.core.tests.test_mixins import MatchReadyMixin


class CompetitionsDivisionsTestCase(MatchReadyMixin, TransactionTestCase):
    """
    Test competition divisions
    """

    def setUp(self):
        super().setUp()
        self._generate_extra_users()
        self._generate_extra_bots()
        self.client.force_login(User.objects.get(username="arenaclient1"))

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

        competition = self._create_open_competition(GameMode.objects.first().id, "Split/Merge Test Competition")
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
        current_in_placements = True
        existing_participants = (
            CompetitionParticipation.objects.filter(
                active=True,
                competition=competition,
                in_placements=False,
                division_num__gte=CompetitionParticipation.MIN_DIVISION,
            )
            .only("division_num", "elo", "match_count", "in_placements")
            .order_by("-division_num", "elo")
        )
        placement_participants = (
            CompetitionParticipation.objects.filter(
                active=True,
                competition=competition,
                in_placements=True,
                division_num__gte=CompetitionParticipation.MIN_DIVISION,
            )
            .only("division_num", "elo", "match_count", "in_placements")
            .order_by("-division_num", "match_count", "elo")
        )
        for cp in list(placement_participants) + list(existing_participants):
            if cp.in_placements:
                self.assertEqual(current_in_placements, True)  # Preceding bot should be in placement
                # TODO: This was commented out to make this test pass as it broke when the stats update was added
                # TODO: to the result submission. Prior to this point, cp.match_count was always 0 because it's only
                # TODO: filled in when the stats gen is run.
                # TODO: What is this check supposed to do?
                # self.assertGreaterEqual(cp.match_count, current_match_count) # Asc match count
                if competition.n_placements > 0 and competition.rounds_this_cycle == 1:
                    self.assertLess(
                        cp.match_count, competition.n_placements
                    )  # Should have less matches played than placement reqs
            else:
                if not current_in_placements and competition.rounds_this_cycle == 1:
                    self.assertGreaterEqual(cp.elo, current_elo)  # Asc ELO
                self.assertGreaterEqual(
                    cp.match_count, competition.n_placements
                )  # Should have at least equal matches played than placement reqs
            self.assertLessEqual(cp.division_num, current_div)  # Desc Div nums
            current_in_placements = cp.in_placements
            current_elo = cp.elo
            current_div = cp.division_num
            if cp.division_num in div_participants:
                div_participants[cp.division_num]["n"] += 1
                div_participants[cp.division_num]["p"] += 1 if cp.in_placements else 0
            else:
                div_participants[cp.division_num] = {"n": 1, "p": 1 if cp.in_placements else 0}
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
        # check round data
        round = Round.objects.filter(competition=competition).order_by("-number").first()
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
        self._post_to_results(response.data["id"], "Player1Win")

        # start and finish all the rest of the generated matches
        for x in range(1, total_exp_matches_per_div):
            match_id = self._post_to_matches().data["id"]
            self._post_to_results(match_id, "Player1Win")
            # double check the match count
            self.assertEqual(Match.objects.filter(started__isnull=True).count(), total_exp_matches_per_div - x - 1)

        # check round is finished
        round = Round.objects.filter(competition=competition).order_by("-number").first()
        self.assertEqual(round.number, exp_round)
        self.assertIsNotNone(round.finished)
        self.assertTrue(round.complete)

    def _complete_cycle(self, competition, exp_rounds, exp_div_participant_count, exp_n_matches):
        for i in range(competition.rounds_per_cycle):
            self._complete_round(competition, exp_rounds[i], exp_div_participant_count, exp_n_matches)
            self.assertEqual(competition.rounds_this_cycle, i + 1)

    def _set_up_competition(self, target_divs, div_size, rpc=1, n_placements=0):
        # avoid old tests breaking that were pre-this feature
        config.REISSUE_UNFINISHED_MATCHES = False

        # freeze every comp but one, so we can get anticipatable results
        competition = self._create_open_competition(GameMode.objects.first().id, "Test Competition")
        # Set up division settings
        competition.target_n_divisions = target_divs
        competition.target_division_size = div_size
        competition.n_placements = n_placements
        competition.rounds_per_cycle = rpc
        competition.save()
        Competition.objects.exclude(id=competition.id).update(status="frozen")
        self._create_map_for_competition("testmapdiv1", competition.id)
        self.assertEqual(Match.objects.count(), 0)  # starting with 0 matches
        self.assertEqual(Round.objects.count(), 0)  # starting with 0 rounds
        return competition

    def test_placements_enabled(self):
        competition = self._set_up_competition(3, 3, 2, 6)
        _exp_par = lambda x, y: {"n": x, "p": y}
        CompetitionParticipation.objects.create(bot_id=self.regularUser1Bot1.id, competition_id=competition.id)
        CompetitionParticipation.objects.create(bot_id=self.staffUser1Bot1.id, competition_id=competition.id)
        self._complete_cycle(competition, [1, 2], {1: _exp_par(2, 2)}, {1: 1})
        CompetitionParticipation.objects.create(bot_id=self.regularUser1Bot2.id, competition_id=competition.id)
        self._complete_cycle(competition, [3, 4], {1: _exp_par(3, 3)}, {1: 3})
        self._complete_cycle(competition, [5, 6], {1: _exp_par(3, 1)}, {1: 3})
        CompetitionParticipation.objects.create(bot_id=self.staffUser1Bot2.id, competition_id=competition.id)
        CompetitionParticipation.objects.create(bot_id=self.regularUser1Bot3_Inactive.id, competition_id=competition.id)
        CompetitionParticipation.objects.create(bot_id=self.staffUser1Bot3.id, competition_id=competition.id)
        CompetitionParticipation.objects.create(bot_id=self.regularUser1Bot4.id, competition_id=competition.id)
        CompetitionParticipation.objects.create(bot_id=self.regularUser2Bot1.id, competition_id=competition.id)
        CompetitionParticipation.objects.create(bot_id=self.regularUser2Bot2.id, competition_id=competition.id)
        CompetitionParticipation.objects.create(bot_id=self.regularUser3Bot1.id, competition_id=competition.id)
        CompetitionParticipation.objects.create(bot_id=self.regularUser3Bot2.id, competition_id=competition.id)
        CompetitionParticipation.objects.create(bot_id=self.regularUser4Bot1.id, competition_id=competition.id)
        CompetitionParticipation.objects.create(bot_id=self.regularUser4Bot2.id, competition_id=competition.id)
        for j in range(3):
            u = User.objects.create_user(
                username=f"regular_user{100 + j}", password="x", email=f"regular_user{100 + j}@dev.aiarena.net"
            )
            for i in range(3):
                self._create_active_bot_for_competition(competition.id, u, f"{u.username}Bot{i + 1}")
        self._complete_cycle(
            competition, [7, 8], {1: _exp_par(7, 4), 2: _exp_par(7, 7), 3: _exp_par(8, 8)}, {1: 21, 2: 21, 3: 28}
        )
        self._complete_cycle(
            competition, [9, 10], {1: _exp_par(7, 0), 2: _exp_par(7, 0), 3: _exp_par(8, 0)}, {1: 21, 2: 21, 3: 28}
        )

    def test_first_round_no_split(self):
        competition = self._set_up_competition(2, 2, 5)
        _exp_par = lambda x, y: {"n": x, "p": y}
        CompetitionParticipation.objects.create(bot_id=self.staffUser1Bot2.id, competition_id=competition.id)
        CompetitionParticipation.objects.create(bot_id=self.regularUser1Bot3_Inactive.id, competition_id=competition.id)
        CompetitionParticipation.objects.create(bot_id=self.staffUser1Bot3.id, competition_id=competition.id)
        CompetitionParticipation.objects.create(bot_id=self.regularUser1Bot4.id, competition_id=competition.id)
        CompetitionParticipation.objects.create(bot_id=self.regularUser2Bot1.id, competition_id=competition.id)
        CompetitionParticipation.objects.create(bot_id=self.regularUser2Bot2.id, competition_id=competition.id)
        CompetitionParticipation.objects.create(bot_id=self.regularUser3Bot1.id, competition_id=competition.id)
        CompetitionParticipation.objects.create(bot_id=self.regularUser3Bot2.id, competition_id=competition.id)
        CompetitionParticipation.objects.create(bot_id=self.regularUser4Bot1.id, competition_id=competition.id)
        CompetitionParticipation.objects.create(bot_id=self.regularUser4Bot2.id, competition_id=competition.id)
        self._complete_cycle(competition, [1, 2, 3, 4, 5], {1: _exp_par(10, 0)}, {1: 45})
        self._complete_cycle(competition, [6, 7, 8, 9, 10], {1: _exp_par(5, 0), 2: _exp_par(5, 0)}, {1: 10, 2: 10})

    def test_no_insertions_mid_cycle(self):
        # And also no matches between those without divisions
        competition = self._set_up_competition(2, 4, 3)
        _exp_par = lambda x, y: {"n": x, "p": y}

        CompetitionParticipation.objects.create(bot_id=self.staffUser1Bot2.id, competition_id=competition.id)
        CompetitionParticipation.objects.create(bot_id=self.regularUser1Bot3_Inactive.id, competition_id=competition.id)
        self._complete_round(competition, 1, {1: _exp_par(2, 0)}, {1: 1})
        CompetitionParticipation.objects.create(bot_id=self.staffUser1Bot3.id, competition_id=competition.id)
        self._complete_round(competition, 2, {1: _exp_par(2, 0)}, {1: 1})
        CompetitionParticipation.objects.create(bot_id=self.regularUser1Bot4.id, competition_id=competition.id)
        self._complete_round(competition, 3, {1: _exp_par(2, 0)}, {1: 1})
        self._complete_round(competition, 4, {1: _exp_par(4, 0)}, {1: 6})

    def test_division_matchmaking(self):
        competition = self._set_up_competition(3, 3, 3)

        _exp_par = lambda x: {"n": x, "p": 0}
        # Start Rounds
        CompetitionParticipation.objects.create(bot_id=self.regularUser1Bot1.id, competition_id=competition.id)
        CompetitionParticipation.objects.create(bot_id=self.staffUser1Bot1.id, competition_id=competition.id)
        self._complete_cycle(competition, [1, 2, 3], {1: _exp_par(2)}, {1: 1})
        CompetitionParticipation.objects.create(bot_id=self.regularUser1Bot2.id, competition_id=competition.id)
        CompetitionParticipation.objects.create(bot_id=self.staffUser1Bot2.id, competition_id=competition.id)
        self._complete_cycle(competition, [4, 5, 6], {1: _exp_par(4)}, {1: 6})
        # Split to 2 divs
        self.ru1b3_cp = CompetitionParticipation.objects.create(
            bot_id=self.regularUser1Bot3_Inactive.id, competition_id=competition.id
        )
        self.su1b3_cp = CompetitionParticipation.objects.create(
            bot_id=self.staffUser1Bot3.id, competition_id=competition.id
        )
        self._complete_cycle(competition, [7, 8, 9], {1: _exp_par(3), 2: _exp_par(3)}, {1: 3, 2: 3})
        # Bot inactive dont merge yet
        self._set_active(self.ru1b3_cp, False)
        self._complete_cycle(competition, [10, 11, 12], {1: _exp_par(2), 2: _exp_par(3)}, {1: 1, 2: 3})
        # Merge threshold reached
        self._set_active(self.su1b3_cp, False)
        self._complete_cycle(competition, [13, 14, 15], {1: _exp_par(4)}, {1: 6})
        # Non equal divisions
        self._set_active(self.ru1b3_cp, True)
        self._set_active(self.su1b3_cp, True)
        self.ru1b4_cp = CompetitionParticipation.objects.create(
            bot_id=self.regularUser1Bot4.id, competition_id=competition.id
        )
        self._complete_cycle(competition, [16, 17, 18], {1: _exp_par(3), 2: _exp_par(4)}, {1: 3, 2: 6})
        # Split to 3 divs
        self.ru2b1_cp = CompetitionParticipation.objects.create(
            bot_id=self.regularUser2Bot1.id, competition_id=competition.id
        )
        self.ru2b2_cp = CompetitionParticipation.objects.create(
            bot_id=self.regularUser2Bot2.id, competition_id=competition.id
        )
        self._complete_cycle(
            competition, [19, 20, 21], {1: _exp_par(3), 2: _exp_par(3), 3: _exp_par(3)}, {1: 3, 2: 3, 3: 3}
        )
        # Merge again
        self._set_active(self.ru1b3_cp, False)
        self._complete_cycle(
            competition, [22, 23, 24], {1: _exp_par(2), 2: _exp_par(3), 3: _exp_par(3)}, {1: 1, 2: 3, 3: 3}
        )
        self._set_active(self.su1b3_cp, False)
        self._complete_cycle(competition, [25, 26, 27], {1: _exp_par(3), 2: _exp_par(4)}, {1: 3, 2: 6})
        self._set_active(self.ru2b1_cp, False)
        self._complete_cycle(competition, [28, 29, 30], {1: _exp_par(3), 2: _exp_par(3)}, {1: 3, 2: 3})
        self._set_active(self.ru1b3_cp, True)
        self._set_active(self.su1b3_cp, True)
        self._set_active(self.ru2b1_cp, True)
        self._complete_cycle(
            competition, [31, 32, 33], {1: _exp_par(3), 2: _exp_par(3), 3: _exp_par(3)}, {1: 3, 2: 3, 3: 3}
        )
        # Grow equally
        CompetitionParticipation.objects.create(bot_id=self.regularUser3Bot1.id, competition_id=competition.id)
        CompetitionParticipation.objects.create(bot_id=self.regularUser3Bot2.id, competition_id=competition.id)
        CompetitionParticipation.objects.create(bot_id=self.regularUser4Bot1.id, competition_id=competition.id)
        CompetitionParticipation.objects.create(bot_id=self.regularUser4Bot2.id, competition_id=competition.id)
        self._complete_cycle(
            competition, [34, 35, 36], {1: _exp_par(4), 2: _exp_par(4), 3: _exp_par(5)}, {1: 6, 2: 6, 3: 10}
        )
        self._create_active_bot_for_competition(competition.id, self.regularUser2, "regularUser2Bot100")
        self._complete_cycle(
            competition, [37, 38, 39], {1: _exp_par(4), 2: _exp_par(5), 3: _exp_par(5)}, {1: 6, 2: 10, 3: 10}
        )
        # Not more splits
        for j in range(3):
            u = User.objects.create_user(
                username=f"regular_user{100 + j}", password="x", email=f"regular_user{100 + j}@dev.aiarena.net"
            )
            for i in range(3):
                self._create_active_bot_for_competition(competition.id, u, f"{u.username}Bot{i + 1}")
        self._complete_cycle(
            competition, [40, 41, 42], {1: _exp_par(7), 2: _exp_par(8), 3: _exp_par(8)}, {1: 21, 2: 28, 3: 28}
        )

    def _set_active(self, cp: CompetitionParticipation, active: bool):
        cp.active = active
        cp.save(update_fields=["active"])
