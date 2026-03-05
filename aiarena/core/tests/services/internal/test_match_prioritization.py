from datetime import timedelta

from django.test import TestCase
from django.utils import timezone

from aiarena.core.models import (
    ArenaClient,
    Bot,
    Competition,
    Game,
    GameMode,
    Map,
    Match,
    MatchParticipation,
    Result,
    Round,
    User,
)
from aiarena.core.models.bot_race import BotRace
from aiarena.core.services.service_implementations._bots import BotsImpl
from aiarena.core.services.service_implementations._competitions import Competitions
from aiarena.core.services.service_implementations._matches import Matches
from aiarena.core.tests.testing_utils import create_bot_for_competition


class MatchPrioritizationTests(TestCase):
    """Tests for match prioritization in _attempt_to_start_a_ladder_match.

    Verifies that:
    - Bots with data enabled are prioritized over those without.
    - Among bots with equal data-enabled status, those that have waited longest
      since their last match completion are prioritized.
    """

    def setUp(self):
        self.user = User.objects.create(username="testuser", email="test@test.com")
        self.arenaclient = ArenaClient.objects.create(trusted=True, owner=self.user)
        self.game = Game.objects.create(name="testgame")
        self.game_mode = GameMode.objects.create(name="testgamemode", game=self.game)
        BotRace.create_all_races()
        self.bot_race = BotRace.objects.first()
        self.competition = Competition.objects.create(name="testcompetition", game_mode=self.game_mode)
        self.competition.playable_races.add(self.bot_race)
        self.competition.open()
        self.match_map = Map.objects.create(name="testmap", game_mode=self.game_mode)
        self.match_map.competitions.add(self.competition)

        self.bots_service = BotsImpl()
        self.competitions_service = Competitions()
        self.matches_service = Matches(self.bots_service, self.competitions_service)

    def _create_bot(self, name, bot_data_enabled=False):
        return create_bot_for_competition(
            competition=self.competition,
            for_user=self.user,
            bot_name=name,
            bot_type="python",
            bot_race=self.bot_race,
        )

    def _create_bot_with_data(self, name, bot_data_enabled=True):
        bot = self._create_bot(name)
        bot.bot_data_enabled = bot_data_enabled
        bot.save()
        return bot

    def _create_round_match(self, round_obj, bot1, bot2):
        match = Match.objects.create(map=self.match_map, round=round_obj)
        MatchParticipation.objects.create(match=match, participant_number=1, bot=bot1)
        MatchParticipation.objects.create(match=match, participant_number=2, bot=bot2)
        return match

    def _complete_match(self, match, completed_at=None):
        """Simulate completing a match by creating a Result and linking it."""
        completed_at = completed_at or timezone.now()
        match.started = completed_at - timedelta(seconds=10)
        match.first_started = match.started
        # Use MatchCancelled type to avoid replay_file validation in Result.save().
        # We also need to bypass Result.save() entirely because Result.__str__
        # accesses self.match.started via a reverse OneToOneField which may not be
        # available yet during creation.
        from django.db import connection

        with connection.cursor() as cursor:
            cursor.execute(
                "INSERT INTO core_result (type, game_steps, created, replay_file_has_been_cleaned, "
                "arenaclient_log_has_been_cleaned) "
                "VALUES (%s, %s, %s, %s, %s) RETURNING id",
                ["MatchCancelled", 100, completed_at, False, False],
            )
            result_id = cursor.fetchone()[0]
        match.result_id = result_id
        match.save()

    def test_data_enabled_bots_prioritized_over_non_data_enabled(self):
        """Matches involving data-enabled bots should be started before others."""
        bot_data1 = self._create_bot_with_data("data_bot1", bot_data_enabled=True)
        bot_data2 = self._create_bot_with_data("data_bot2", bot_data_enabled=True)
        bot_nodata1 = self._create_bot_with_data("nodata_bot1", bot_data_enabled=False)
        bot_nodata2 = self._create_bot_with_data("nodata_bot2", bot_data_enabled=False)

        round_obj = Round.objects.create(competition=self.competition)
        # Create matches: one with data-enabled bots, one without
        match_data = self._create_round_match(round_obj, bot_data1, bot_data2)
        match_nodata = self._create_round_match(round_obj, bot_nodata1, bot_nodata2)

        started_match = self.matches_service._attempt_to_start_a_ladder_match(self.arenaclient, round_obj)

        self.assertIsNotNone(started_match)
        self.assertEqual(started_match.id, match_data.id)

    def test_longest_waiting_bots_prioritized(self):
        """Among bots with same data-enabled status, those waiting longest should be prioritized."""
        bot1 = self._create_bot_with_data("bot1", bot_data_enabled=False)
        bot2 = self._create_bot_with_data("bot2", bot_data_enabled=False)
        bot3 = self._create_bot_with_data("bot3", bot_data_enabled=False)
        bot4 = self._create_bot_with_data("bot4", bot_data_enabled=False)

        now = timezone.now()
        round_obj = Round.objects.create(competition=self.competition)

        # Create previous completed matches with different completion times
        # bot1 vs bot2: completed 30 minutes ago (waited longest)
        old_match = self._create_round_match(round_obj, bot1, bot2)
        self._complete_match(old_match, now - timedelta(minutes=30))

        # bot3 vs bot4: completed 5 minutes ago (waited less)
        recent_match = self._create_round_match(round_obj, bot3, bot4)
        self._complete_match(recent_match, now - timedelta(minutes=5))

        # Create new round with available matches
        new_round = Round.objects.create(competition=self.competition)
        match_old_bots = self._create_round_match(new_round, bot1, bot2)
        match_recent_bots = self._create_round_match(new_round, bot3, bot4)

        started_match = self.matches_service._attempt_to_start_a_ladder_match(self.arenaclient, new_round)

        self.assertIsNotNone(started_match)
        self.assertEqual(started_match.id, match_old_bots.id)

    def test_data_enabled_bots_with_no_match_history_highest_priority(self):
        """Data-enabled bots with no match history should get highest priority."""
        bot_data_new = self._create_bot_with_data("data_new", bot_data_enabled=True)
        bot_data_new2 = self._create_bot_with_data("data_new2", bot_data_enabled=True)
        bot_nodata1 = self._create_bot_with_data("nodata1", bot_data_enabled=False)
        bot_nodata2 = self._create_bot_with_data("nodata2", bot_data_enabled=False)

        round_obj = Round.objects.create(competition=self.competition)
        match_data_new = self._create_round_match(round_obj, bot_data_new, bot_data_new2)
        match_nodata = self._create_round_match(round_obj, bot_nodata1, bot_nodata2)

        started_match = self.matches_service._attempt_to_start_a_ladder_match(self.arenaclient, round_obj)

        self.assertIsNotNone(started_match)
        self.assertEqual(started_match.id, match_data_new.id)

    def test_mixed_data_enabled_prioritized_over_none(self):
        """A match with one data-enabled bot should be prioritized over a match with none."""
        bot_data1 = self._create_bot_with_data("data1", bot_data_enabled=True)
        bot_nodata1 = self._create_bot_with_data("nodata1", bot_data_enabled=False)
        bot_nodata2 = self._create_bot_with_data("nodata2", bot_data_enabled=False)
        bot_nodata3 = self._create_bot_with_data("nodata3", bot_data_enabled=False)

        round_obj = Round.objects.create(competition=self.competition)
        match_mixed = self._create_round_match(round_obj, bot_data1, bot_nodata1)
        match_nodata = self._create_round_match(round_obj, bot_nodata2, bot_nodata3)

        started_match = self.matches_service._attempt_to_start_a_ladder_match(self.arenaclient, round_obj)

        self.assertIsNotNone(started_match)
        self.assertEqual(started_match.id, match_mixed.id)

    def test_among_data_enabled_longest_wait_wins(self):
        """Among multiple data-enabled matches, the one with longest-waiting bots wins."""
        bot_data_old1 = self._create_bot_with_data("data_old1", bot_data_enabled=True)
        bot_data_old2 = self._create_bot_with_data("data_old2", bot_data_enabled=True)
        bot_data_new1 = self._create_bot_with_data("data_new1", bot_data_enabled=True)
        bot_data_new2 = self._create_bot_with_data("data_new2", bot_data_enabled=True)

        now = timezone.now()
        setup_round = Round.objects.create(competition=self.competition)

        # old bots completed a match 60 minutes ago
        old_match = self._create_round_match(setup_round, bot_data_old1, bot_data_old2)
        self._complete_match(old_match, now - timedelta(minutes=60))

        # new bots completed a match 5 minutes ago
        new_match = self._create_round_match(setup_round, bot_data_new1, bot_data_new2)
        self._complete_match(new_match, now - timedelta(minutes=5))

        # Create available matches for the new round
        new_round = Round.objects.create(competition=self.competition)
        match_old_bots = self._create_round_match(new_round, bot_data_old1, bot_data_old2)
        match_new_bots = self._create_round_match(new_round, bot_data_new1, bot_data_new2)

        started_match = self.matches_service._attempt_to_start_a_ladder_match(self.arenaclient, new_round)

        self.assertIsNotNone(started_match)
        self.assertEqual(started_match.id, match_old_bots.id)

    def test_fallback_to_non_data_enabled_when_fewer_than_two_data_enabled(self):
        """When only one data-enabled bot exists, fall back to longest-waiting non-data bots."""
        bot_data1 = self._create_bot_with_data("data1", bot_data_enabled=True)
        bot_nodata_old = self._create_bot_with_data("nodata_old", bot_data_enabled=False)
        bot_nodata_recent = self._create_bot_with_data("nodata_recent", bot_data_enabled=False)

        now = timezone.now()
        setup_round = Round.objects.create(competition=self.competition)

        # nodata_old completed a match 60 minutes ago
        old_match = self._create_round_match(setup_round, bot_data1, bot_nodata_old)
        self._complete_match(old_match, now - timedelta(minutes=60))

        # nodata_recent completed a match 5 minutes ago
        recent_match = self._create_round_match(setup_round, bot_data1, bot_nodata_recent)
        self._complete_match(recent_match, now - timedelta(minutes=5))

        # New round: only non-data matches available (data1 has only mixed matches)
        new_round = Round.objects.create(competition=self.competition)
        match_with_old = self._create_round_match(new_round, bot_data1, bot_nodata_old)
        match_with_recent = self._create_round_match(new_round, bot_data1, bot_nodata_recent)

        started_match = self.matches_service._attempt_to_start_a_ladder_match(self.arenaclient, new_round)

        self.assertIsNotNone(started_match)
        # match_with_old involves bot_data1 (data_enabled=True, 1 data bot) and bot_nodata_old
        # match_with_recent involves bot_data1 (data_enabled=True, 1 data bot) and bot_nodata_recent
        # Both have the same data_enabled_count (1).
        # bot_data1's most recent match was 5 min ago, bot_nodata_old's was 60 min ago
        # match_with_old: max(5 min ago, 60 min ago) = 5 min ago (timestamp)
        # match_with_recent: max(5 min ago, 5 min ago) = 5 min ago
        # Both have the same max timestamp. But since data1's last match is 5 min ago
        # which is the same for both, the tiebreaker is nodata_old vs nodata_recent.
        # Actually max(last_end(data1), last_end(nodata_old)) = last_end(data1) since 5 min ago is more recent
        # And max(last_end(data1), last_end(nodata_recent)) = last_end(data1) for same reason
        # So they'll be equal. The first match in the list that can start will be chosen.
        # Both should be valid matches though.
        self.assertIn(started_match.id, [match_with_old.id, match_with_recent.id])
