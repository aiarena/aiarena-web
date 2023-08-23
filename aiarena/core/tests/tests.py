import json
import os
from datetime import timedelta
from io import StringIO

from django.core import serializers
from django.core.exceptions import ValidationError
from django.core.files import File
from django.core.management import CommandError, call_command
from django.test import TestCase, TransactionTestCase
from django.utils import timezone

from constance import config

from aiarena.core.api import Ladders, Matches
from aiarena.core.management.commands import cleanupreplays
from aiarena.core.models import (
    Bot,
    Competition,
    CompetitionParticipation,
    Map,
    Match,
    MatchParticipation,
    Result,
    Round,
    User,
)
from aiarena.core.models.bot_race import BotRace
from aiarena.core.models.game_mode import GameMode
from aiarena.core.tests.test_mixins import BaseTestMixin, FullDataSetMixin, LoggedInMixin, MatchReadyMixin
from aiarena.core.tests.testing_utils import TestAssetPaths
from aiarena.core.utils import calculate_md5


# Use this to pre-build a fuller dataset for testing


class UtilsTestCase(BaseTestMixin, TestCase):
    def test_calc_md5(self):
        filename = os.path.join(os.path.dirname(os.path.realpath(__file__)), "test-media/../test-media/test_bot.zip")
        self.assertEqual("c96bcfc79318a8b50b0b2c8696400d06", calculate_md5(filename))


class BotTestCase(LoggedInMixin, TestCase):
    def test_bot_creation_and_update(self):
        self.test_client.login(self.staffUser1)

        # required for active bot
        competition = self._create_game_mode_and_open_competition()

        # test max bots for user
        for i in range(0, config.MAX_USER_BOT_COUNT):
            if i < config.MAX_USER_BOT_PARTICIPATIONS_ACTIVE_FREE_TIER:
                self._create_active_bot_for_competition(competition.id, self.regularUser1, "testbot{0}".format(i))
            else:
                self._create_bot(self.regularUser1, "testbot{0}".format(i))
        with self.assertRaisesMessage(
            ValidationError,
            "Maximum bot count of {0} already reached. "
            "No more bots may be added for this user.".format(config.MAX_USER_BOT_COUNT),
        ):
            self._create_bot(self.regularUser1, "testbot{0}".format(config.MAX_USER_BOT_COUNT))

        bot1 = Bot.objects.first()

        # test display id regen
        prev_bot_display_id = bot1.game_display_id
        bot1.regen_game_display_id()
        self.assertNotEqual(bot1.game_display_id, prev_bot_display_id)

        bot1.refresh_from_db()
        # check hashes
        self.assertEqual(TestAssetPaths.test_bot_zip_hash, bot1.bot_zip_md5hash)
        self.assertEqual(TestAssetPaths.test_bot_datas["bot1"][0]["hash"], bot1.bot_data_md5hash)

        # check the bot file now exists
        self.assertTrue(os.path.isfile("./private-media/bots/{0}/bot_zip".format(bot1.id)))

        with open(TestAssetPaths.test_bot_zip_path, "rb") as bot_zip:
            bot1.bot_zip = File(bot_zip)
            bot1.save()

        # check the bot file backup now exists
        self.assertTrue(os.path.isfile("./private-media/bots/{0}/bot_zip_backup".format(bot1.id)))

        # test active bots per race limit for user
        # this shouldn't trip the validation
        inactive_bot = Bot.objects.filter(user=self.regularUser1, competition_participations__isnull=True).first()
        cp = CompetitionParticipation.objects.create(competition=competition, bot=inactive_bot, active=False)
        cp.full_clean()

        # this should trip the validation
        with self.assertRaisesMessage(
            ValidationError,
            "Too many active participations already exist for this user."
            " You are allowed 4 active participations in competitions.",
        ):
            cp = CompetitionParticipation.objects.create(competition=competition, bot=inactive_bot, active=True)
            cp.full_clean()

        # test updating bot_zip
        with open(TestAssetPaths.test_bot_zip_updated_path, "rb") as bot_zip_updated:
            bot1.bot_zip = File(bot_zip_updated)
            bot1.save()

        bot1.refresh_from_db()
        self.assertEqual(TestAssetPaths.test_bot_zip_updated_hash, bot1.bot_zip_md5hash)

        # test updating bot_data
        # using bot2's data instead here so it's different
        with open(TestAssetPaths.test_bot_datas["bot2"][0]["path"], "rb") as bot_data_updated:
            bot1.bot_data = File(bot_data_updated)
            bot1.save()

        bot1.refresh_from_db()
        self.assertEqual(TestAssetPaths.test_bot_datas["bot2"][0]["hash"], bot1.bot_data_md5hash)


class MatchTagsTestCase(MatchReadyMixin, TestCase):
    """
    Test submission of match tags
    """

    def _send_tags(self, bot1_tags, bot2_tags, results_resp_code=201):
        match_response = self._post_to_matches()
        self.assertEqual(match_response.status_code, 201)
        result_response = self._post_to_results(
            match_response.data["id"], "Player1Win", bot1_tags=bot1_tags, bot2_tags=bot2_tags
        )
        self.assertEqual(result_response.status_code, results_resp_code)
        return (match_response, result_response)

    def test_results_with_tags(self):
        az_symbols = "abcdefghijklmnopqrstuvwxyz"
        num_symbols = "0123456789"
        extra_symbols = " _ _ "
        game_mode = GameMode.objects.first()

        # No tags
        Matches.request_match(self.staffUser1, self.staffUser1Bot2, self.regularUser1Bot1, game_mode=game_mode)
        match_response, result_response = self._send_tags(None, None)
        self.assertTrue(Match.objects.get(id=match_response.data["id"]).tags.all().count() == 0)

        # 1 side tags
        Matches.request_match(self.staffUser1, self.staffUser1Bot2, self.regularUser1Bot1, game_mode=game_mode)
        match_response, result_response = self._send_tags(["abc"], None)
        match_tags = Match.objects.get(id=match_response.data["id"]).tags.all()
        self.assertTrue(match_tags.count() == 1)
        for mt in match_tags:
            self.assertEqual(mt.user.websiteuser, self.staffUser1)

        Matches.request_match(self.staffUser1, self.staffUser1Bot2, self.regularUser1Bot1, game_mode=game_mode)
        match_response, result_response = self._send_tags(None, ["abc"])
        match_tags = Match.objects.get(id=match_response.data["id"]).tags.all()
        self.assertTrue(match_tags.count() == 1)
        for mt in match_tags:
            self.assertEqual(mt.user.websiteuser, self.regularUser1)

        # Check that tags are correct, stripped and attributed to the correct user
        _temp_tag1 = "tes1t_ test2"
        _temp_tags = [az_symbols, num_symbols, extra_symbols, _temp_tag1]
        bot1_tags_list = [_temp_tags, [_temp_tag1]]
        bot2_tags_list = [[_temp_tag1], _temp_tags]
        for i in range(2):
            Matches.request_match(self.regularUser1, self.regularUser1Bot1, self.staffUser1Bot1, game_mode=game_mode)
            match_response, _ = self._send_tags(bot1_tags_list[i], bot2_tags_list[i])
            match = Match.objects.get(id=match_response.data["id"])
            user1 = match.participant1.bot.user
            user2 = match.participant2.bot.user
            tag_matched = [False, False, False]
            user_matched = [False, False]
            match_tags = match.tags.all()
            # Total recorded tags are correct
            self.assertEqual(match_tags.count(), len(bot1_tags_list[i] + bot2_tags_list[i]))
            for mt in match_tags:
                # If common tag, make sure its the correct user
                if mt.tag.name == _temp_tag1:
                    if mt.user == user1:
                        user_matched[0] = True
                    elif mt.user == user2:
                        user_matched[1] = True
                else:
                    if i == 0:
                        self.assertEqual(mt.user, user1)
                    elif i == 1:
                        self.assertEqual(mt.user, user2)
                    # Tags that are not common
                    if mt.tag.name == az_symbols:
                        tag_matched[0] = True
                    elif mt.tag.name == num_symbols:
                        tag_matched[1] = True
                    # Check that whitespace is stripped
                    elif mt.tag.name == extra_symbols.strip():
                        tag_matched[2] = True
            self.assertTrue(all(tag_matched))
            self.assertTrue(all(user_matched))

        # Check that if both bots belong to the same user, tags unioned
        bot1_tags = _temp_tags
        bot2_tags = [_temp_tag1, "qwerty"]
        Matches.request_match(self.staffUser1, self.staffUser1Bot2, self.staffUser1Bot1, game_mode=game_mode)
        match_response, _ = self._send_tags(bot1_tags, bot2_tags)
        match = Match.objects.get(id=match_response.data["id"])
        match_tags = match.tags.all()
        # Total recorded tags are correct
        self.assertEqual(match_tags.count(), len(set(bot1_tags) | set(bot2_tags)))

        # Check that invalid tags get processed to be valid rather than causing validation errors
        # This is to prevent tags from causing a result to fail submission
        Matches.request_match(self.staffUser1, self.staffUser1Bot2, self.regularUser1Bot1, game_mode=game_mode)
        match_response, result_response = self._send_tags(
            bot1_tags=["!", "2", "A", "", az_symbols + num_symbols + extra_symbols], bot2_tags=["123"]
        )
        match_tags = Match.objects.get(id=match_response.data["id"]).tags.all()
        tags_matched = ["2", "a", "abcdefghijklmnopqrstuvwxyz012345", "123"]
        self.assertTrue(match_tags.count() == 4)

        # Too many tags
        Matches.request_match(self.staffUser1, self.staffUser1Bot2, self.regularUser1Bot1, game_mode=game_mode)
        match_response, result_response = self._send_tags(
            bot1_tags=[str(i) for i in range(50)], bot2_tags=[str(i) for i in range(50)]
        )
        match_tags = Match.objects.get(id=match_response.data["id"]).tags.all()
        self.assertTrue(match_tags.count() == 64)


class CompetitionsTestCase(FullDataSetMixin, TransactionTestCase):
    """
    Test competition rotation
    """

    def _finish_competition_rounds(self, exclude_competition_id):
        for x in range(
            Match.objects.exclude(round__competition_id=exclude_competition_id).filter(result__isnull=True).count()
        ):
            response = self._post_to_matches()
            self.assertEqual(response.status_code, 201)

            response = self._post_to_results(response.data["id"], "Player1Win")
            self.assertEqual(response.status_code, 201)

    def test_competition_states(self):
        # self.test_client.login(self.arenaclientUser1)

        # freeze competition2, so we can get anticipatable results
        competition1 = Competition.objects.filter(status="open").first()
        competition2 = Competition.objects.exclude(id=competition1.id).get()
        competition2.freeze()

        self.assertEqual(
            Match.objects.exclude(round__competition_id=competition2.id).filter(result__isnull=True).count(),
            19,
            msg="This test expects 19 unplayed matches in order to work.",
        )

        # cache the bots - list forces the queryset to be evaluated
        bots = list(Bot.objects.all())

        # Freeze the competition - now we shouldn't receive any new matches
        competition1.freeze()

        # play all the requested matches
        for i in range(Match.objects.filter(requested_by__isnull=False).count()):
            response = self._post_to_matches()
            self.assertEqual(response.status_code, 201)
            response = self._post_to_results(response.data["id"], "Player1Win")
            self.assertEqual(response.status_code, 201)

        response = self._post_to_matches()
        self.assertEqual(response.status_code, 200)
        self.assertEqual("No game available for client.", response.data["detail"])

        # Pause the competition and finish the round
        competition1.pause()

        self._finish_competition_rounds(competition2.id)

        # this should fail due to a new round trying to generate while the competition is paused
        with self.assertLogs(logger="aiarena.api.arenaclient.ac_coordinator", level="DEBUG") as log:
            response = self._post_to_matches()
            self.assertEqual(response.status_code, 200)
            self.assertEqual("No game available for client.", response.data["detail"])
            self.assertIn(
                f"DEBUG:aiarena.api.arenaclient.ac_coordinator:Skipping competition {competition1.id}: "
                f"This competition is paused.",
                log.output,
            )

        # reopen the competition
        competition1.open()

        # start a new round
        response = self._post_to_matches()
        self.assertEqual(response.status_code, 201)

        competition1.start_closing()

        # Activating a bot should now fail
        with self.assertRaisesMessage(ValidationError, "That competition is not accepting new participants."):
            bot = Bot.objects.filter(competition_participations__isnull=True).first()
            cp = CompetitionParticipation(competition=competition1, bot=bot)
            cp.full_clean()  # causes validation to run

        # finish the competition
        self._finish_competition_rounds(competition2.id)

        # successful close
        competition1.refresh_from_db()
        self.assertEqual(competition1.status, "closed")

        # participants should be deactivated now
        for cp in CompetitionParticipation.objects.filter(competition=competition1):
            self.assertFalse(cp.active)

        # Activating a bot should fail
        with self.assertRaisesMessage(ValidationError, "That competition is not accepting new participants."):
            bot = Bot.objects.filter(competition_participations__isnull=True).first()
            cp = CompetitionParticipation(competition=competition1, bot=bot)
            cp.full_clean()  # causes validation to run

        # start a new competition
        competition2 = Competition.objects.create(game_mode=GameMode.objects.first())

        # no currently available competitions
        response = self._post_to_matches()
        self.assertEqual(response.status_code, 200)
        self.assertEqual("No game available for client.", response.data["detail"])

        # active bots
        for bot in Bot.objects.all():
            CompetitionParticipation.objects.create(bot=bot, competition=competition2)

        # current competition is paused
        response = self._post_to_matches()
        self.assertEqual(response.status_code, 200)
        self.assertEqual("No game available for client.", response.data["detail"])

        competition2.open()

        # check no bot display IDs have changed
        # they used to change in previous website versions - make sure they no longer do
        for bot in bots:
            updated_bot = Bot.objects.get(id=bot.id)
            self.assertEqual(updated_bot.game_display_id, bot.game_display_id)

        # no maps
        with self.assertLogs(logger="aiarena.api.arenaclient.ac_coordinator", level="DEBUG") as log:
            response = self._post_to_matches()
            self.assertEqual(response.status_code, 200)
            self.assertEqual("No game available for client.", response.data["detail"])
            self.assertIn(
                f"DEBUG:aiarena.api.arenaclient.ac_coordinator:Skipping competition {competition2.id}: "
                f"There are no active maps available for a match.",
                log.output,
            )

        map = Map.objects.first()
        map.competitions.add(competition2)

        # start a new round
        response = self._post_to_matches()
        self.assertEqual(response.status_code, 201)

        # New round should be number 1 for the new competition
        round = Round.objects.get(competition=competition2)
        self.assertEqual(round.number, 1)

    def test_competition_race_restriction(self):
        # self.client.force_login(self.arenaclientUser1)

        User.objects.update(extra_active_competition_participations=99)  # avoid this restriction

        terran = BotRace.terran()
        zerg = BotRace.zerg()
        competition = self._create_open_competition(
            GameMode.objects.first().id, "Race Restricted Competition", {terran.id}
        )

        with self.assertRaisesMessage(
            ValidationError, "This competition is restricted to the following bot races: Terran"
        ):
            a_zerg_bot = Bot.objects.filter(plays_race=zerg).first()
            cp = CompetitionParticipation.objects.create(bot=a_zerg_bot, competition=competition)
            cp.full_clean()  # causes validation to run

        a_terran_bot = Bot.objects.filter(plays_race=terran).first()
        cp = CompetitionParticipation.objects.create(bot=a_terran_bot, competition=competition)
        cp.full_clean()  # causes validation to run


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
        self.assertEqual(response.status_code, 201)
        match_id = response.data["id"]

        out = StringIO()
        call_command("cancelmatches", match_id, stdout=out)
        self.assertIn('Successfully marked match "{0}" with MatchCancelled'.format(match_id), out.getvalue())

        # test result already exists
        with self.assertRaisesMessage(CommandError, 'A result already exists for match "{0}"'.format(match_id)):
            call_command("cancelmatches", match_id)

        # test that cancelling the match marks it as started.
        self.assertIsNotNone(Match.objects.get(id=match_id).started)

        response = self._post_to_matches()
        self.assertEqual(response.status_code, 201)
        active_match_id = response.data["id"]
        out = StringIO()
        call_command("cancelmatches", "--active", stdout=out)
        self.assertIn('Successfully marked match "{0}" with MatchCancelled'.format(active_match_id), out.getvalue())

        # cancel the rest of the matches.
        # start at 2 because we already cancelled some above
        for x in range(2, expectedMatchCountPerRound):
            response = self._post_to_matches()
            self.assertEqual(response.status_code, 201)
            match_id = response.data["id"]

            out = StringIO()
            call_command("cancelmatches", match_id, stdout=out)
            self.assertIn('Successfully marked match "{0}" with MatchCancelled'.format(match_id), out.getvalue())

            # test result already exists
            with self.assertRaisesMessage(CommandError, 'A result already exists for match "{0}"'.format(match_id)):
                call_command("cancelmatches", match_id)

            # test that cancelling the match marks it as started.
            self.assertIsNotNone(Match.objects.get(id=match_id).started)

        # check that the round was correctly marked as finished
        round = Match.objects.get(id=match_id).round
        self.assertTrue(round.complete)
        self.assertIsNotNone(round.finished)

    def test_cleanup_replays_and_logs(self):
        NUM_MATCHES = 12
        self.test_client.login(self.staffUser1)

        # freeze competition2, so we can get anticipatable results
        competition1 = Competition.objects.filter(status="open").first()
        competition2 = Competition.objects.exclude(id=competition1.id).get()
        competition2.freeze()

        # generate some matches so we have replays to delete...
        for x in range(NUM_MATCHES):  # 12 = two rounds
            response = self._post_to_matches()
            self.assertEqual(response.status_code, 201, f"{response.status_code} {response.data}")
            match_id = response.data["id"]
            self._post_to_results(match_id, "Player1Win")

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
        call_command("cleanupreplays", stdout=out)
        self.assertIn(
            "Cleaning up replays starting from 30 days into the past...\nGathering records to clean...\n{0} records gathered.\nCleaned up {0} replays.".format(
                NUM_MATCHES
            ),
            out.getvalue(),
        )

        # ensure the job doesn't re-clean the same records when run again
        out = StringIO()
        call_command("cleanupreplays", stdout=out)
        self.assertIn(
            "Cleaning up replays starting from 30 days into the past...\nGathering records to clean...\n0 records gathered.\nCleaned up 0 replays.",
            out.getvalue(),
        )

        self.assertEqual(results.count(), NUM_MATCHES)
        for result in results:
            self.assertFalse(result.replay_file)

        out = StringIO()
        call_command("cleanuparenaclientlogfiles", stdout=out)
        self.assertIn(
            "Cleaning up arena client logfiles starting from 30 days into the past...\nGathering records to clean...\n{0} records gathered.\nCleaned up {0} logfiles.".format(
                NUM_MATCHES
            ),
            out.getvalue(),
        )

        # ensure the job doesn't re-clean the same records when run again
        out = StringIO()
        call_command("cleanuparenaclientlogfiles", stdout=out)
        self.assertIn(
            "Cleaning up arena client logfiles starting from 30 days into the past...\nGathering records to clean...\n0 records gathered.\nCleaned up 0 logfiles.",
            out.getvalue(),
        )

        self.assertEqual(results.count(), NUM_MATCHES)
        for result in results:
            self.assertFalse(result.replay_file)

        out = StringIO()
        call_command("cleanupmatchlogfiles", stdout=out)
        self.assertIn(
            "Cleaning up match logfiles starting from 30 days into the past...\nGathering records to clean...\n{0} records gathered.\nCleaned up {0} logfiles.".format(
                NUM_MATCHES * 2
            ),
            out.getvalue(),
        )

        # ensure the job doesn't re-clean the same records when run again
        out = StringIO()
        call_command("cleanupmatchlogfiles", stdout=out)
        self.assertIn(
            "Cleaning up match logfiles starting from 30 days into the past...\nGathering records to clean...\n0 records gathered.\nCleaned up 0 logfiles.",
            out.getvalue(),
        )

        self.assertEqual(participants.count(), NUM_MATCHES * 2)
        for participant in participants:
            self.assertFalse(participant.match_log)

    def test_generatestats(self):
        self._generate_full_data_set()
        out = StringIO()
        call_command("generatestats", stdout=out)
        self.assertIn("Done", out.getvalue())

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
                "json", Ladders.get_competition_last_round_participants(competition)
            )

            # make sure it matches the known working method
            pre_finalization_ranks_legacy = serializers.serialize(
                "json", Ladders.get_competition_last_round_participants_legacy(competition)
            )
            self.assertEqual(_sort_json(pre_finalization_ranks), _sort_json(pre_finalization_ranks_legacy))

            # fake competition closure
            competition.status = "closed"
            competition.save()

            out = StringIO()
            call_command("finalizecompetition", "--competitionid", competition.id, stdout=out)
            self.assertIn(f"Competition {competition.id} has been finalized.", out.getvalue())

            post_finalization_ranks = serializers.serialize(
                "json", Ladders.get_competition_last_round_participants(competition)
            )
            self.assertEqual(pre_finalization_ranks, post_finalization_ranks)

            # make sure it matches the known working method
            post_finalization_ranks_legacy = serializers.serialize(
                "json", Ladders.get_competition_last_round_participants_legacy(competition)
            )
            self.assertEqual(_sort_json(post_finalization_ranks), _sort_json(post_finalization_ranks_legacy))

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
        self.assertTrue(match1.result is not None)
