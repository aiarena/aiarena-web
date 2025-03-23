from django.test import TransactionTestCase

from constance import config

from aiarena.core.models import Competition, CompetitionParticipation, Match, Result, Round, User
from aiarena.core.tests.test_mixins import MatchReadyMixin


class RoundRobinGenerationTestCase(MatchReadyMixin, TransactionTestCase):
    def setUp(self):
        super().setUp()
        self.client.force_login(User.objects.get(username="arenaclient1"))

    def test_round_robin_generation(self):
        # avoid old tests breaking that were pre-this feature
        config.REISSUE_UNFINISHED_MATCHES = False

        # freeze every comp but one, so we can get anticipatable results
        active_comp = Competition.objects.filter(status="open").first()
        Competition.objects.exclude(id=active_comp.id).update(status="frozen")

        # we need to deactivate a bot midway through the test, so we'll activate this one for now
        bot_to_deactivate = CompetitionParticipation.objects.create(
            bot_id=self.regularUser1Bot3_Inactive.id, competition_id=active_comp.id
        )
        bot_to_deactivate.active = True
        bot_to_deactivate.save()

        bot_count = CompetitionParticipation.objects.filter(active=True, competition=active_comp).count()
        bot_count_after_deactivation = bot_count - 1
        expected_matches = lambda bc: int(bc / 2 * (bc - 1))
        expected_match_count_per_round = expected_matches(bot_count)
        expected_match_count_per_round_after_bot_deactivated = expected_matches(bot_count_after_deactivation)
        self.assertGreater(bot_count, 1)  # check we have more than 1 bot

        self.assertEqual(Match.objects.count(), 0)  # starting with 0 matches
        self.assertEqual(Round.objects.count(), 0)  # starting with 0 rounds

        # Validate that participated_in_most_recent_round flags have not been set yet
        self.assertTrue(
            CompetitionParticipation.objects.filter(
                competition=active_comp, participated_in_most_recent_round=True
            ).count()
            == 0
        )

        response = self._post_to_matches()  # this should trigger a new round robin generation

        # Validate that participated_in_most_recent_round flags have now been set
        self.assertTrue(
            CompetitionParticipation.objects.filter(
                competition=active_comp, participated_in_most_recent_round=True
            ).count()
            == bot_count
        )

        # check match count
        self.assertEqual(Match.objects.count(), expected_match_count_per_round)

        # check round data
        self.assertEqual(Round.objects.count(), 1)
        round1 = Round.objects.get()  # get the only round
        self.assertIsNotNone(round1.started)
        self.assertIsNone(round1.finished)
        self.assertFalse(round1.complete)

        # finish the initial match
        self._post_to_results(response.data["id"], "Player1Win")

        # start and finish all the rest of the generated matches
        for x in range(1, expected_match_count_per_round):
            match_id = self._post_to_matches().data["id"]
            self._post_to_results(match_id, "Player1Win")
            # double check the match count
            self.assertEqual(Match.objects.filter(started__isnull=True).count(), expected_match_count_per_round - x - 1)

        # check round is finished
        self.assertEqual(Round.objects.count(), 1)
        round1.refresh_from_db()
        self.assertIsNotNone(round1.finished)
        self.assertTrue(round1.complete)

        # Repeat again but with quirks

        match_id = self._post_to_matches().data["id"]  # this should trigger another new round robin generation

        # Validate that participated_in_most_recent_round flags are still set properly
        self.assertTrue(
            CompetitionParticipation.objects.filter(
                competition=active_comp, participated_in_most_recent_round=True
            ).count()
            == bot_count
        )

        # check match count
        self.assertEqual(Match.objects.count(), expected_match_count_per_round * 2)

        # check round data
        self.assertEqual(Round.objects.count(), 2)
        round2 = Round.objects.get(id=round1.id + 1)
        self.assertIsNotNone(round2.started)
        self.assertIsNone(round2.finished)
        self.assertFalse(round2.complete)

        # finish the initial match
        self._post_to_results(match_id, "Player1Win")

        # start and finish all except one the rest of the generated matches
        for x in range(1, expected_match_count_per_round - 1):
            match_id = self._post_to_matches().data["id"]
            self._post_to_results(match_id, "Player1Win")
            # double check the match count
            self.assertEqual(Match.objects.filter(started__isnull=True).count(), expected_match_count_per_round - x - 1)

        # at this stage there should be one unstarted match left
        self.assertEqual(Match.objects.filter(started__isnull=True).count(), 1)

        # start the last match
        response2ndRoundLastMatch = self._post_to_matches()
        self.assertEqual(response2ndRoundLastMatch.status_code, 201)
        self.assertEqual(Match.objects.filter(started__isnull=True).count(), 0)

        # deactivate a bot so that we can check it's participated_in_most_recent_round field is updated appropriately
        bot_to_deactivate.active = False
        bot_to_deactivate.save(update_fields=["active"])

        # the following part ensures round generation is properly handled when an old round is not yet finished
        self._post_to_matches()

        # Validate that participated_in_most_recent_round flags reflect the deactivated bot
        self.assertTrue(
            CompetitionParticipation.objects.filter(
                competition=active_comp, participated_in_most_recent_round=True
            ).count()
            == bot_count - 1
        )
        bot_to_deactivate.refresh_from_db()
        self.assertFalse(bot_to_deactivate.participated_in_most_recent_round)

        self.assertEqual(
            Match.objects.filter(started__isnull=True).count(), expected_match_count_per_round_after_bot_deactivated - 1
        )
        total_expected_match_count = (
            expected_match_count_per_round * 2
        ) + expected_match_count_per_round_after_bot_deactivated
        self.assertEqual(Match.objects.count(), total_expected_match_count)

        # check round data
        self.assertEqual(Round.objects.count(), 3)

        # check 2nd round data is still the same
        round2.refresh_from_db()
        self.assertIsNotNone(round2.started)
        self.assertIsNone(round2.finished)
        self.assertFalse(round2.complete)

        # check 3rd round data
        round3 = Round.objects.get(id=round2.id + 1)
        self.assertIsNotNone(round3.started)
        self.assertIsNone(round3.finished)
        self.assertFalse(round3.complete)

        # now finish the 2nd round
        self._post_to_results(response2ndRoundLastMatch.data["id"], "Player1Win")

        # check round is finished
        round2.refresh_from_db()
        self.assertIsNotNone(round2.finished)
        self.assertTrue(round2.complete)

        # check 3rd round data remains unmodified
        round3.refresh_from_db()
        self.assertIsNotNone(round3.started)
        self.assertIsNone(round3.finished)
        self.assertFalse(round3.complete)

        # check result count - should have 2 rounds worth of results
        self.assertEqual(Result.objects.count(), expected_match_count_per_round * 2)
