import json
from datetime import timedelta
from io import StringIO

from django.core import serializers
from django.core.management import CommandError, call_command
from django.test import TransactionTestCase
from django.utils import timezone

from constance import config

from aiarena.core.management.commands import doglobalfilecleanup
from aiarena.core.models import (
    Bot,
    Competition,
    CompetitionParticipation,
    Match,
    MatchParticipation,
    Result,
    User,
)
from aiarena.core.services import ladders
from aiarena.core.tests.test_mixins import MatchReadyMixin


class ManagementCommandTests(MatchReadyMixin, TransactionTestCase):
    """
    Tests for management commands
    """

    def test_cancel_matches(self):
        # freeze competition2, so we can get anticipatable results
        competition1 = Competition.objects.filter(status="open").first()
        competition2 = Competition.objects.exclude(id=competition1.id).get()
        competition2.freeze()

        count = CompetitionParticipation.objects.filter(competition_id=competition1.id, active=True).count()
        expectedMatchCountPerRound = int(count / 2 * (count - 1))

        # test match doesn't exist
        with self.assertRaisesMessage(CommandError, 'Match "12345" does not exist'):
            call_command("cancelmatches", "12345")

        # test match successfully cancelled
        self.client.login(username="staff_user", password="x")
        response = self._post_to_matches()
        match_id = response.data["id"]

        out = StringIO()
        call_command("cancelmatches", match_id, stdout=out)
        self.assertIn(f'Successfully marked match "{match_id}" with MatchCancelled', out.getvalue())

        # test result already exists
        with self.assertRaisesMessage(CommandError, f'A result already exists for match "{match_id}"'):
            call_command("cancelmatches", match_id)

        # test that cancelling the match marks it as started.
        self.assertIsNotNone(Match.objects.get(id=match_id).started)

        response = self._post_to_matches()
        active_match_id = response.data["id"]
        out = StringIO()
        call_command("cancelmatches", "--active", stdout=out)
        self.assertIn(f'Successfully marked match "{active_match_id}" with MatchCancelled', out.getvalue())

        # cancel the rest of the matches.
        # start at 2 because we already cancelled some above
        for x in range(2, expectedMatchCountPerRound):
            response = self._post_to_matches()
            match_id = response.data["id"]

            out = StringIO()
            call_command("cancelmatches", match_id, stdout=out)
            self.assertIn(f'Successfully marked match "{match_id}" with MatchCancelled', out.getvalue())

            # test result already exists
            with self.assertRaisesMessage(CommandError, f'A result already exists for match "{match_id}"'):
                call_command("cancelmatches", match_id)

            # test that cancelling the match marks it as started.
            self.assertIsNotNone(Match.objects.get(id=match_id).started)

        # check that the round was correctly marked as finished
        round = Match.objects.get(id=match_id).round
        self.assertTrue(round.complete)
        self.assertIsNotNone(round.finished)

    def test_doglobalfilecleanup(self):
        NUM_MATCHES = 12
        participants, results = self._generate_files_to_cleanup(NUM_MATCHES)

        out = StringIO()
        call_command("doglobalfilecleanup", stdout=out)
        self.assertIn(
            "Cleaning up result files starting from 30 days into the past...\n"
            "Gathering records to clean...\n"
            "12 records gathered.\n",
            out.getvalue(),
        )
        self.assertIn(
            "Cleaning up match logfiles starting from 30 days into the past...\n"
            "Gathering records to clean...\n"
            f"{NUM_MATCHES * 2} records gathered.\n",
            out.getvalue(),
        )

        # ensure the job doesn't re-clean the same records when run again
        out = StringIO()
        call_command("doglobalfilecleanup", stdout=out)
        self.assertIn(
            "Cleaning up result files starting from 30 days into the past...\n"
            "Gathering records to clean...\n"
            "0 records gathered.\n",
            out.getvalue(),
        )
        self.assertIn(
            "Cleaning up match logfiles starting from 30 days into the past...\n"
            "Gathering records to clean...\n"
            "0 records gathered.\n",
            out.getvalue(),
        )

        self.assertEqual(results.count(), NUM_MATCHES)
        for result in results:
            self.assertFalse(result.replay_file)

        self.assertEqual(participants.count(), NUM_MATCHES * 2)
        for participant in participants:
            self.assertFalse(participant.match_log)

    def _generate_files_to_cleanup(self, num_matches: int):
        self.test_client.login(self.staffUser1)
        # freeze competition2, so we can get anticipatable results
        competition1 = Competition.objects.filter(status="open").first()
        competition2 = Competition.objects.exclude(id=competition1.id).get()
        competition2.freeze()
        # generate some matches so we have replays to delete...
        for x in range(num_matches):  # 12 = two rounds
            response = self._post_to_matches()
            match_id = response.data["id"]
            self._post_to_results(match_id, "Player1Win")
        # double check the replay and log files exist
        results = Result.objects.filter(replay_file__isnull=False)
        self.assertEqual(results.count(), num_matches)
        # after we ensure the arena client log count matches, we can safely just use the above results list
        results_logs = Result.objects.filter(arenaclient_log__isnull=False)
        self.assertEqual(results_logs.count(), num_matches)
        participants = MatchParticipation.objects.filter(match_log__isnull=False)
        self.assertEqual(participants.count(), num_matches * 2)
        # set the created time so they'll be purged
        results.update(created=timezone.now() - timedelta(days=doglobalfilecleanup.Command._DEFAULT_DAYS_LOOKBACK + 1))
        return participants, results

    def test_generatestats(self):
        self._generate_full_data_set()
        out = StringIO()
        call_command("generatestats", stdout=out)
        self.assertIn("Done", out.getvalue())

    def test_generatestats_graphsonly(self):
        self._generate_full_data_set()
        out = StringIO()
        call_command("generatestats", "--graphsonly", stdout=out)
        self.assertIn("Done", out.getvalue())

    def test_generatestats_graphsonly_invalid_call(self):
        self._generate_full_data_set()
        out = StringIO()
        competition_id = Competition.objects.first().id
        with self.assertRaisesMessage(CommandError, "--graphsonly is not valid with --finalize"):
            call_command("generatestats", "--graphsonly", "--competitionid", competition_id, "--finalize", stdout=out)

    def test_finalizecompetition(self):
        def _sort_json(json_str: str):
            json_list = json.loads(json_str)
            return sorted(json_list, key=lambda x: x["pk"])

        self._generate_full_data_set()

        for competition in Competition.objects.all():
            call_command("generatestats", "--competitionid", competition.id, "--finalize")

        for competition in Competition.objects.all():
            with self.assertRaisesMessage(
                CommandError,
                f"Competition {competition.id} is not closed! It must be closed before it can be finalized.",
            ):
                out = StringIO()
                call_command("finalizecompetition", "--competitionid", competition.id, stdout=out)

            # The front end uses get_competition_last_round_participants for displaying a closed competition's rankings
            # so here we test that the displayed ranks don't change after finalization
            pre_finalization_ranks = serializers.serialize(
                "json", ladders.get_competition_last_round_participants(competition)
            )

            # fake competition closure
            competition.status = "closed"
            competition.save()

            out = StringIO()
            call_command("finalizecompetition", "--competitionid", competition.id, stdout=out)
            self.assertIn(f"Competition {competition.id} has been finalized.", out.getvalue())

            post_finalization_ranks = serializers.serialize(
                "json", ladders.get_competition_last_round_participants(competition)
            )
            self.assertEqual(pre_finalization_ranks, post_finalization_ranks)

            out = StringIO()
            call_command("finalizecompetition", "--competitionid", competition.id, stdout=out)
            self.assertIn(f"WARNING: Competition {competition.id} is already finalized. Skipping...", out.getvalue())

    def test_generatestats_competition(self):
        self._generate_full_data_set()
        out = StringIO()
        for competition in Competition.objects.all():
            call_command("generatestats", "--competitionid", competition.id, stdout=out)
        self.assertIn("Done", out.getvalue())

    def test_generatestats_competition_finalize(self):
        self._generate_full_data_set()
        for competition in Competition.objects.all():
            out = StringIO()
            call_command("generatestats", "--competitionid", competition.id, "--finalize", stdout=out)
            self.assertIn("Done", out.getvalue())

        # these should all fail
        for competition in Competition.objects.all():
            out = StringIO()
            call_command("generatestats", "--competitionid", competition.id, stdout=out)
            self.assertIn("WARNING: Skipping competition", out.getvalue())

        for competition in Competition.objects.all():
            out = StringIO()
            call_command("generatestats", "--competitionid", competition.id, "--finalize", stdout=out)
            self.assertIn("WARNING: Skipping competition", out.getvalue())

    def test_generatestats_finalize_invalid(self):
        with self.assertRaisesMessage(CommandError, "--finalize is only valid with --competitionid"):
            call_command("generatestats", "--finalize")

        with self.assertRaisesMessage(CommandError, "--finalize is only valid with --competitionid"):
            call_command("generatestats", "--allcompetitions", "--finalize")

    def test_generatestats_bot(self):
        self._generate_full_data_set()
        out = StringIO()
        for bot in Bot.objects.all():
            call_command("generatestats", "--botid", bot.id, stdout=out)
        self.assertIn("Done", out.getvalue())

    def test_seed(self):
        out = StringIO()
        call_command("seed", stdout=out)
        self.assertIn('Done. User logins have a password of "x".', out.getvalue())

    def test_seed_integration_tests(self):
        out = StringIO()
        call_command("seed_integration_tests", stdout=out)
        self.assertIn('Done. User logins have a password of "x".', out.getvalue())

    def test_check_bot_hashes(self):
        call_command("checkbothashes")

    def test_repair_bot_hashes(self):
        call_command("repairbothashes")

    def test_timeout_overtime_matches(self):
        self.test_client.login(User.objects.get(username="arenaclient1"))

        response = self.client.post("/api/arenaclient/matches/")
        self.assertEqual(response.status_code, 201)

        # save the match for modification
        match1 = Match.objects.get(id=response.data["id"])

        # set the created time back into the past long enough for it to cause a time out
        match1.first_started = timezone.now() - (config.TIMEOUT_MATCHES_AFTER + timedelta(hours=1))
        match1.save()

        # this should trigger the bots to be forced out of the match
        call_command("timeoutovertimematches")

        # confirm a result was registered
        match1.refresh_from_db()
        self.assertTrue(match1.result is not None)
