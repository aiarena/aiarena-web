import os

from django.core.exceptions import ValidationError
from django.core.files import File
from django.test import TestCase, TransactionTestCase

from constance import config

from aiarena import settings
from aiarena.core.models import (
    Bot,
    Competition,
    CompetitionParticipation,
    Map,
    Match,
    Round,
    User,
)
from aiarena.core.models.bot_race import BotRace
from aiarena.core.models.game_mode import GameMode
from aiarena.core.services import match_requests
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
            if i < settings.MAX_USER_BOT_PARTICIPATIONS_ACTIVE_FREE_TIER:
                self._create_active_bot_for_competition(competition.id, self.regularUser1, f"testbot{i}")
            else:
                self._create_bot(self.regularUser1, f"testbot{i}")
        with self.assertRaisesMessage(
            ValidationError,
            f"Maximum bot count of {config.MAX_USER_BOT_COUNT} already reached. "
            "No more bots may be added for this user.",
        ):
            self._create_bot(self.regularUser1, f"testbot{config.MAX_USER_BOT_COUNT}")

        bot1 = Bot.objects.first()

        bot1.refresh_from_db()
        # check hashes
        self.assertEqual(TestAssetPaths.test_bot_zip_hash, bot1.bot_zip_md5hash)
        self.assertEqual(TestAssetPaths.test_bot_datas["bot1"][0]["hash"], bot1.bot_data_md5hash)

        with open(TestAssetPaths.test_bot_zip_path, "rb") as bot_zip:
            bot1.bot_zip = File(bot_zip)
            bot1.save()

        # test active bots per race limit for user
        # this shouldn't trip the validation
        inactive_bot = Bot.objects.filter(user=self.regularUser1, competition_participations__isnull=True).first()
        cp = CompetitionParticipation.objects.create(competition=competition, bot=inactive_bot, active=False)
        cp.full_clean()

        """
        Try to activate a bot for a user that already has 4 active participations
        """
        with self.assertRaisesMessage(
            ValidationError,
            "Too many active participations already exist for this user."
            " You are allowed 4 active participations in competitions.",
        ):
            cp.active = True
            cp.full_clean()  # causes validation to run

        """
        Try to join a bot to a new competition for a user that already has 4 active participations
        """
        game_mode = GameMode.objects.get()
        another_competition = self._create_open_competition(game_mode.id, name="Another Competition")
        with self.assertRaisesMessage(
            ValidationError,
            "Too many active participations already exist for this user."
            " You are allowed 4 active participations in competitions.",
        ):
            cp = CompetitionParticipation.objects.create(competition=another_competition, bot=inactive_bot, active=True)
            cp.full_clean()  # causes validation to run

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
        match_requests.request_match(self.staffUser1, self.staffUser1Bot2, self.regularUser1Bot1, game_mode=game_mode)
        match_response, result_response = self._send_tags(None, None)
        self.assertTrue(Match.objects.get(id=match_response.data["id"]).tags.all().count() == 0)

        # 1 side tags
        match_requests.request_match(self.staffUser1, self.staffUser1Bot2, self.regularUser1Bot1, game_mode=game_mode)
        match_response, result_response = self._send_tags(["abc"], None)
        match_tags = Match.objects.get(id=match_response.data["id"]).tags.all()
        self.assertTrue(match_tags.count() == 1)
        for mt in match_tags:
            self.assertEqual(mt.user.websiteuser, self.staffUser1)

        match_requests.request_match(self.staffUser1, self.staffUser1Bot2, self.regularUser1Bot1, game_mode=game_mode)
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
            match_requests.request_match(
                self.regularUser1, self.regularUser1Bot1, self.staffUser1Bot1, game_mode=game_mode
            )
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
        match_requests.request_match(self.staffUser1, self.staffUser1Bot2, self.staffUser1Bot1, game_mode=game_mode)
        match_response, _ = self._send_tags(bot1_tags, bot2_tags)
        match = Match.objects.get(id=match_response.data["id"])
        match_tags = match.tags.all()
        # Total recorded tags are correct
        self.assertEqual(match_tags.count(), len(set(bot1_tags) | set(bot2_tags)))

        # Check that invalid tags get processed to be valid rather than causing validation errors
        # This is to prevent tags from causing a result to fail submission
        match_requests.request_match(self.staffUser1, self.staffUser1Bot2, self.regularUser1Bot1, game_mode=game_mode)
        match_response, result_response = self._send_tags(
            bot1_tags=["!", "2", "A", "", az_symbols + num_symbols + extra_symbols], bot2_tags=["123"]
        )
        match_tags = Match.objects.get(id=match_response.data["id"]).tags.all()
        self.assertTrue(match_tags.count() == 4)

        # Too many tags
        match_requests.request_match(self.staffUser1, self.staffUser1Bot2, self.regularUser1Bot1, game_mode=game_mode)
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
            match_id = self._post_to_matches().data["id"]
            self._post_to_results(match_id, "Player1Win")

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
            match_id = self._post_to_matches().data["id"]
            self._post_to_results(match_id, "Player1Win")

        response = self._post_to_matches(expected_code=200)
        self.assertEqual("No game available for client.", response.data["detail"])

        # Pause the competition and finish the round
        competition1.pause()

        self._finish_competition_rounds(competition2.id)

        # this should fail due to a new round trying to generate while the competition is paused
        with self.assertLogs(logger="aiarena.api.arenaclient.common.ac_coordinator", level="DEBUG") as log:
            response = self._post_to_matches(expected_code=200)
            self.assertEqual("No game available for client.", response.data["detail"])
            self.assertIn(
                f"DEBUG:aiarena.api.arenaclient.common.ac_coordinator:Skipping competition {competition1.id}: "
                f"This competition is paused.",
                log.output,
            )

        # reopen the competition
        competition1.open()

        # start a new round
        self._post_to_matches()

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
        response = self._post_to_matches(expected_code=200)
        self.assertEqual("No game available for client.", response.data["detail"])

        # active bots
        for bot in Bot.objects.all():
            CompetitionParticipation.objects.create(bot=bot, competition=competition2)

        # current competition is paused
        response = self._post_to_matches(expected_code=200)
        self.assertEqual("No game available for client.", response.data["detail"])

        competition2.open()

        # check no bot display IDs have changed
        # they used to change in previous website versions - make sure they no longer do
        for bot in bots:
            updated_bot = Bot.objects.get(id=bot.id)
            self.assertEqual(updated_bot.game_display_id, bot.game_display_id)

        # no maps
        with self.assertLogs(logger="aiarena.api.arenaclient.common.ac_coordinator", level="DEBUG") as log:
            response = self._post_to_matches(expected_code=200)
            self.assertEqual("No game available for client.", response.data["detail"])
            self.assertIn(
                f"DEBUG:aiarena.api.arenaclient.common.ac_coordinator:Skipping competition {competition2.id}: "
                f"There are no active maps available for a match.",
                log.output,
            )

        map = Map.objects.first()
        map.competitions.add(competition2)

        # start a new round
        self._post_to_matches()

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
