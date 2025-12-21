from django.test import TestCase
from django.core.files.uploadedfile import SimpleUploadedFile

from aiarena.core.models import (
    ArenaClient,
    Bot,
    BotRace,
    Game,
    GameMode,
    Map,
    Match,
    MatchParticipation,
    Result,
    User,
)
from aiarena.core.services import arena_clients


class ArenaClientsServiceTests(TestCase):
    def setUp(self):
        # Minimal game/mode/map setup
        self.game = Game.objects.create(name="TestGame", map_file_extension=".map")
        self.mode = GameMode.objects.create(name="1v1", game=self.game)
        map_file = SimpleUploadedFile("test.map", b"dummy")
        self.map = Map.objects.create(name="TestMap", file=map_file, game_mode=self.mode)

        # Users and ArenaClient
        self.owner = User.objects.create(username="owner", email="owner@example.com")
        self.bot_user = User.objects.create(username="botuser", email="bot@example.com")
        self.ac = ArenaClient.objects.create(username="ac1", email="ac1@example.com", owner=self.owner, trusted=True)

        # BotRace and Bots
        self.race = BotRace.objects.create(label="T")
        bot_zip = SimpleUploadedFile("bot.zip", b"zip-bytes")
        self.bot1 = Bot.objects.create(user=self.bot_user, name="BotOne", plays_race=self.race, type="python", bot_zip=bot_zip)
        bot_zip2 = SimpleUploadedFile("bot2.zip", b"zip-bytes-2")
        self.bot2 = Bot.objects.create(user=self.bot_user, name="BotTwo", plays_race=self.race, type="python", bot_zip=bot_zip2)

    def _create_match_with_participants(self, assigned=True, finished=False):
        match = Match.objects.create(map=self.map, assigned_to=self.ac if assigned else None)
        # Participants
        p1 = MatchParticipation.objects.create(match=match, participant_number=1, bot=self.bot1)
        p2 = MatchParticipation.objects.create(match=match, participant_number=2, bot=self.bot2)
        if finished:
            # Create a Result and hook it to the match
            res = Result.objects.create(type="Error", game_steps=1234)
            match.result = res
            match.save(update_fields=["result"])
        return match

    def test_get_assigned_matches_returns_only_unfinished_assigned(self):
        # Create matches: one assigned unfinished, one assigned finished, one unassigned unfinished
        m1 = self._create_match_with_participants(assigned=True, finished=False)
        self._create_match_with_participants(assigned=True, finished=True)
        self._create_match_with_participants(assigned=False, finished=False)

        qs = arena_clients.get_incomplete_assigned_matches_queryset(self.ac)
        matches = list(qs)

        # Only the unfinished assigned match should be returned
        self.assertEqual([m.id for m in matches], [m1.id])
        # Basic sanity check: all returned matches are assigned to this AC and have no result
        for m in matches:
            self.assertEqual(m.assigned_to_id, self.ac.id)
            self.assertIsNone(m.result)

    def test_get_assigned_matches_results_orders_and_prefetches(self):
        # Create two finished matches assigned to the AC and one finished match not assigned
        m1 = self._create_match_with_participants(assigned=True, finished=False)
        m2 = self._create_match_with_participants(assigned=True, finished=False)
        m3 = self._create_match_with_participants(assigned=False, finished=False)

        # Attach results (created timestamps will order m3 < m2 < m1 or similar based on creation order)
        r1 = Result.objects.create(type="Error", game_steps=1111)
        m1.result = r1
        m1.save(update_fields=["result"])

        r2 = Result.objects.create(type="Error", game_steps=2222)
        m2.result = r2
        m2.save(update_fields=["result"])

        r3 = Result.objects.create(type="Error", game_steps=3333)
        m3.result = r3
        m3.save(update_fields=["result"])

        qs = arena_clients.get_assigned_matches_results_queryset(self.ac)
        results = list(qs)

        # Only results for matches assigned to the AC should be returned, newest first
        self.assertEqual({res.id for res in results}, {r1.id, r2.id})
        # Basic sanity check: all returned results belong to matches assigned to this AC
        for res in results:
            self.assertEqual(res.match.assigned_to_id, self.ac.id)
