from collections.abc import Iterable
from datetime import timedelta

from django.core.cache import cache
from django.test import TransactionTestCase
from django.utils import timezone

from constance import config
from rest_framework.authtoken.models import Token

from aiarena import settings
from aiarena.api.arenaclient.testing_utils import AcApiTestingClient
from aiarena.core.models import ArenaClient, Competition, GameMode, Match, Round
from aiarena.core.models.bot_race import BotRace
from aiarena.core.services import match_requests
from aiarena.core.tests.test_mixins import LoggedInMixin
from aiarena.frontend.admin import CompetitionAdminForm


class ArenaClientLimitTests(LoggedInMixin, TransactionTestCase):
    """Competition.arena_client_limit prefers the earliest claimers and idle-fills the rest."""

    def setUp(self):
        super().setUp()
        settings.MAX_USER_BOT_PARTICIPATIONS_ACTIVE_FREE_TIER = 40
        config.MAX_USER_BOT_COUNT = 40
        config.REISSUE_UNFINISHED_MATCHES = True
        self.test_client.login(self.staffUser1)
        cache.delete("competition_priority_order")
        self.client_a = self.test_ac_api_client
        self.ac_a = self.arenaclientUser1
        self.ac_b, self.client_b = self._new_ac("arenaclient-b")
        self.ac_c, self.client_c = self._new_ac("arenaclient-c")

    def _new_ac(self, username, trusted=True):
        ac = ArenaClient.objects.create(
            username=username,
            email=f"{username}@dev.aiarena.net",
            type="ARENA_CLIENT",
            trusted=trusted,
            owner=self.staffUser1,
        )
        return ac, AcApiTestingClient(api_token=Token.objects.create(user=ac).key)

    def _ensure_game(self):
        if getattr(self, "_game_mode", None) is not None:
            return
        game = self.test_client.create_game("StarCraft II", ".SC2Map")
        self._game_mode = self.test_client.create_gamemode("Melee", game.id)
        BotRace.create_all_races()

    def _make_comp(self, name, bot_count, trusted=True, downloadable=False, limit=None, owner=None):
        self._ensure_game()
        comp = self.test_client.create_competition(name, self._game_mode.id, require_trusted_infrastructure=trusted)
        self.test_client.open_competition(comp.id)
        comp.refresh_from_db()
        # open_competition posts a partial admin form, which would wipe a limit set at create time.
        comp.require_trusted_infrastructure = trusted
        comp.arena_client_limit = limit
        comp.save(update_fields=["require_trusted_infrastructure", "arena_client_limit"])
        self._create_map_for_competition(f"map-{name}", comp.id)
        owner = owner or self.regularUser1
        races = [BotRace.terran(), BotRace.zerg(), BotRace.protoss(), BotRace.random()]
        for index in range(bot_count):
            self._create_active_bot_for_competition(
                comp.id,
                owner,
                f"{name}-bot{index}",
                races[index % len(races)],
                downloadable=downloadable,
            )
        cache.delete("competition_priority_order")
        return comp

    def _match(self, response) -> Match:
        return Match.objects.select_related("round__competition").get(id=response.data["id"])

    def _competition_id(self, response) -> int:
        return self._match(response).round.competition_id

    def _set_limit(self, comp, limit):
        comp.arena_client_limit = limit
        comp.save(update_fields=["arena_client_limit"])

    def _age_result(self, match: Match):
        when = timezone.now() - (config.TIMEOUT_MATCHES_AFTER + timedelta(hours=1))
        match.started = when
        match.first_started = when
        match.save(update_fields=["started", "first_started"])
        match.result.created = when
        match.result.save(update_fields=["created"])

    def _finish(self, client, response_or_id):
        match_id = response_or_id if isinstance(response_or_id, int) else response_or_id.data["id"]
        return client.submit_result(match_id, "Player1Win")

    def _clients(self):
        return {
            self.ac_a.id: self.client_a,
            self.ac_b.id: self.client_b,
            self.ac_c.id: self.client_c,
        }

    def _submit_started(self, comp):
        """Post a result for every started match so the next poll is not a reissue."""
        open_matches = Match.objects.filter(round__competition=comp, result__isnull=True, started__isnull=False)
        for match in list(open_matches):
            self._clients()[match.assigned_to_id].submit_result(match.id, "Player1Win")

    def _play_out(self, client, comp):
        """Submit every match of comp's current rounds until a poll would have to generate another."""
        for _ in range(30):
            if not Round.objects.filter(competition=comp, complete=False, match__result__isnull=True).exists():
                if not Round.objects.filter(competition=comp, complete=False).exists():
                    return
            response = client.post_to_matches()
            match = self._match(response)
            self.assertEqual(match.round.competition_id, comp.id, match.id)
            client.submit_result(match.id, "Player1Win")
            comp.refresh_from_db()

    def test_empty_cap_lets_every_client_claim(self):
        config.REISSUE_UNFINISHED_MATCHES = False
        comp = self._make_comp("Open", bot_count=4)
        self.assertIsNone(comp.arena_client_limit)

        first = self._match(self.client_a.post_to_matches())
        second = self._match(self.client_b.post_to_matches())
        self.assertEqual(first.round.competition_id, comp.id)
        self.assertEqual(second.round.competition_id, comp.id)
        self.assertEqual(first.assigned_to_id, self.ac_a.id)
        self.assertEqual(second.assigned_to_id, self.ac_b.id)
        self.assertNotEqual(first.id, second.id)

    def test_limit_one_skips_outsider_with_other_work_then_idle_fills(self):
        limited = self._make_comp("Limited", bot_count=4, limit=1)
        first = self.client_a.post_to_matches()
        self.assertEqual(self._competition_id(first), limited.id)

        other = self._make_comp("Other", bot_count=2, owner=self.staffUser1)
        outsider = self._match(self.client_b.post_to_matches())
        self.assertEqual(outsider.round.competition_id, other.id)
        self.assertFalse(
            Match.objects.filter(round__competition=limited, assigned_to=self.ac_b).exists(),
        )

        self._finish(self.client_b, outsider.id)
        other.refresh_from_db()
        self.assertTrue(other.round_set.get().complete)
        other.pause()

        filled = self._match(self.client_b.post_to_matches())
        self.assertEqual(filled.round.competition_id, limited.id)
        self.assertEqual(filled.assigned_to_id, self.ac_b.id)
        # Submit it so the next poll is a new choice. Reissue would hand this match back.
        self.client_b.submit_result(filled.id, "Player1Win")

        other.open()
        # A is still non-stale (its match is unfinished), so B is past the limit of 1.
        restored = self._match(self.client_b.post_to_matches())
        self.assertEqual(restored.round.competition_id, other.id)

    def test_limit_two_admits_two_preferred_clients(self):
        limited = self._make_comp("Limited", bot_count=4, limit=2)
        self.assertEqual(self._competition_id(self.client_a.post_to_matches()), limited.id)
        self.assertEqual(self._competition_id(self.client_b.post_to_matches()), limited.id)

        other = self._make_comp("Other", bot_count=2, owner=self.staffUser1)
        other_match = self._match(self.client_c.post_to_matches())
        self.assertEqual(other_match.round.competition_id, other.id)

        # Submit it so the round completes. A paused competition with a finished round
        # has nothing left to start, which is when the idle pass may take Limited.
        # A and B already hold both pairs, so finish A's match before that idle claim.
        self._finish(self.client_c, other_match.id)
        other.pause()
        self._finish(self.client_a, Match.objects.get(assigned_to=self.ac_a, result__isnull=True).id)
        filled = self._match(self.client_c.post_to_matches())
        self.assertEqual(filled.round.competition_id, limited.id)
        self.assertEqual(filled.assigned_to_id, self.ac_c.id)

        # C now holds that pair. Finish B's match so A, still inside the window, can start another.
        self._finish(self.client_b, Match.objects.get(assigned_to=self.ac_b, result__isnull=True).id)
        self.assertEqual(self._competition_id(self.client_a.post_to_matches()), limited.id)

    def test_cap_counts_clients_not_open_matches(self):
        config.REISSUE_UNFINISHED_MATCHES = False
        limited = self._make_comp("Limited", bot_count=4, limit=1)
        first = self._match(self.client_a.post_to_matches())
        second = self._match(self.client_a.post_to_matches())
        self.assertEqual(first.assigned_to_id, self.ac_a.id)
        self.assertEqual(second.assigned_to_id, self.ac_a.id)
        self.assertNotEqual(first.id, second.id)

        other = self._make_comp("Other", bot_count=2, owner=self.staffUser1)
        self.assertEqual(self._competition_id(self.client_b.post_to_matches()), other.id)

        # Other's only match is now in flight and its bots are locked, so B has nothing else to start.
        # Finishing one of A's matches frees a Limited pair for the idle pass.
        self.client_a.submit_result(first.id, "Player1Win")
        self.assertEqual(self._competition_id(self.client_b.post_to_matches()), limited.id)

    def test_reissue_returns_the_same_match(self):
        self._make_comp("Limited", bot_count=2, limit=1)
        first = self.client_a.post_to_matches()
        second = self.client_a.post_to_matches()
        self.assertEqual(first.data["id"], second.data["id"])
        self.assertEqual(self._match(first).assigned_to_id, self.ac_a.id)

    def test_one_client_still_plays_a_full_round(self):
        comp = self._make_comp("Limited", bot_count=4, limit=1)
        expected = 6  # 4 bots, one match per pair
        for _ in range(expected):
            response = self.client_a.post_to_matches()
            self.assertEqual(self._competition_id(response), comp.id)
            self.client_a.submit_result(response.data["id"], "Player1Win")
        self.assertEqual(Match.objects.filter(round__competition=comp).count(), expected)
        self.assertEqual(Round.objects.filter(competition=comp).count(), 1)
        self.assertTrue(Round.objects.get(competition=comp).complete)

    def test_requested_match_is_other_work(self):
        limited = self._make_comp("Limited", bot_count=2, limit=1)
        self.client_a.post_to_matches()
        bot = limited.participations.first().bot
        match_requests.request_match(
            self.regularUser1,
            bot,
            bot.get_random_excluding_self(),
            game_mode=GameMode.objects.get(name="Melee"),
        )
        taken = self._match(self.client_b.post_to_matches())
        self.assertIsNotNone(taken.requested_by_id)
        self.assertFalse(Match.objects.filter(round__competition=limited, assigned_to=self.ac_b).exists())

    def test_preferred_client_takes_a_requested_match_before_the_ladder(self):
        limited = self._make_comp("Limited", bot_count=4, limit=1)
        self._finish(self.client_a, self.client_a.post_to_matches())
        bot = limited.participations.first().bot
        match_requests.request_match(
            self.regularUser1,
            bot,
            bot.get_random_excluding_self(),
            game_mode=self._game_mode,
        )
        taken = self._match(self.client_a.post_to_matches())
        self.assertIsNotNone(taken.requested_by_id)
        self.assertIsNone(taken.round_id)

    def test_preferred_client_plays_another_competition_when_its_own_is_paused(self):
        limited = self._make_comp("Limited", bot_count=2, limit=1)
        self._play_out(self.client_a, limited)
        limited.pause()
        other = self._make_comp("Other", bot_count=2, owner=self.staffUser1)
        self.assertEqual(self._competition_id(self.client_a.post_to_matches()), other.id)

    def test_untrusted_client_cannot_idle_fill_a_trusted_competition(self):
        comp = self._make_comp("Trusted", bot_count=2, trusted=True, limit=2)
        untrusted, client = self._new_ac("arenaclient-untrusted", trusted=False)
        response = client.post_to_matches(expected_code=200)
        self.assertEqual(response.data["detail"].code, "no_game_available")
        self.assertFalse(Match.objects.filter(round__competition=comp, assigned_to=untrusted).exists())

        claimed = self._match(self.client_a.post_to_matches())
        self.assertEqual(claimed.assigned_to_id, self.ac_a.id)
        self.assertEqual(claimed.round.competition_id, comp.id)

    def test_untrusted_competition_shares_one_roster(self):
        limited = self._make_comp("Public", bot_count=4, trusted=False, downloadable=True, limit=1)
        untrusted, untrusted_client = self._new_ac("arenaclient-untrusted", trusted=False)
        self.assertEqual(self._match(untrusted_client.post_to_matches()).assigned_to_id, untrusted.id)

        other = self._make_comp("StaffLadder", bot_count=2, owner=self.staffUser1)
        self.assertEqual(self._competition_id(self.client_b.post_to_matches()), other.id)

        # One started match each. Public is larger, so it is offered first, and B is outside
        # the limit of 1. The preferred pass skips Public and plays StaffLadder again.
        self._finish(self.client_b, Match.objects.get(assigned_to=self.ac_b).id)
        self.assertEqual(self._competition_id(self.client_b.post_to_matches()), other.id)
        self._finish(self.client_b, Match.objects.get(assigned_to=self.ac_b, result__isnull=True).id)
        other.pause()

        filled = self._match(self.client_b.post_to_matches())
        self.assertEqual(filled.round.competition_id, limited.id)
        self.assertEqual(filled.assigned_to_id, self.ac_b.id)
        # Submit it so the next poll is a new claim, not a reissue. Started matches are now even,
        # Public stays first, and raising the limit puts B inside the window.
        self.client_b.submit_result(filled.id, "Player1Win")

        self._set_limit(limited, 2)
        other.open()
        self.assertEqual(self._competition_id(self.client_b.post_to_matches()), limited.id)

    def test_raising_the_limit_unmasks_the_next_claimer(self):
        limited = self._make_comp("Limited", bot_count=4, limit=1)
        self._finish(self.client_a, self.client_a.post_to_matches())
        other = self._make_comp("Other", bot_count=2, owner=self.staffUser1)
        other_held = self._match(self.client_b.post_to_matches())
        self.assertEqual(other_held.round.competition_id, other.id)

        # A second Other match keeps its recent share from tying Limited's. C is outside the
        # window, so the preferred pass skips Limited.
        self.client_b.submit_result(other_held.id, "Player1Win")
        other_held = self._match(self.client_c.post_to_matches())
        self.assertEqual(other_held.round.competition_id, other.id)

        self._set_limit(limited, 2)
        # B has not claimed Limited, so the wider window admits B on the preferred pass.
        self.assertEqual(self._competition_id(self.client_b.post_to_matches()), limited.id)
        self.client_c.submit_result(other_held.id, "Player1Win")
        self.assertEqual(self._competition_id(self.client_a.post_to_matches()), limited.id)

        _ac_d, client_d = self._new_ac("arenaclient-d")
        # A and B hold Limited, so its bots are locked. D is outside the window and takes Other.
        taken = self._match(client_d.post_to_matches())
        self.assertEqual(taken.round.competition_id, other.id)

    def test_lowering_the_limit_keeps_inflight_matches(self):
        limited = self._make_comp("Limited", bot_count=6, limit=3)
        held = {
            self.ac_a.id: self._match(self.client_a.post_to_matches()),
            self.ac_b.id: self._match(self.client_b.post_to_matches()),
            self.ac_c.id: self._match(self.client_c.post_to_matches()),
        }
        self._set_limit(limited, 1)
        claimants = ((self.client_a, self.ac_a.id), (self.client_b, self.ac_b.id), (self.client_c, self.ac_c.id))
        for client, ac_id in claimants:
            again = self._match(client.post_to_matches())
            self.assertEqual(again.id, held[ac_id].id)
            self.assertEqual(again.assigned_to_id, ac_id)

        other = self._make_comp("Other", bot_count=2, owner=self.staffUser1)
        self.client_b.submit_result(held[self.ac_b.id].id, "Player1Win")
        self.assertEqual(self._competition_id(self.client_b.post_to_matches()), other.id)

        self._finish(self.client_b, Match.objects.get(round__competition=other, result__isnull=True).id)
        other.pause()
        self.assertEqual(self._competition_id(self.client_b.post_to_matches()), limited.id)

        self.client_a.submit_result(held[self.ac_a.id].id, "Player1Win")
        self.assertEqual(self._competition_id(self.client_a.post_to_matches()), limited.id)

    def test_raising_the_limit_again_restores_claim_order(self):
        # Other is played first so it already has a share of recent matches. A competition
        # with every recent match is ordered after a fresh one, whatever its participant count.
        other = self._make_comp("Other", bot_count=4, owner=self.staffUser1)
        for _ in range(3):
            self._finish(self.client_a, self.client_a.post_to_matches())
        limited = self._make_comp("Limited", bot_count=6, limit=3)
        for client in (self.client_a, self.client_b, self.client_c):
            self._finish(client, client.post_to_matches())
        self._set_limit(limited, 1)
        # Only A is preferred. Limited has more participants and a similar recent share, so it is first.
        self.assertEqual(self._competition_id(self.client_a.post_to_matches()), limited.id)
        other_held = self._match(self.client_b.post_to_matches())
        self.assertEqual(other_held.round.competition_id, other.id)

        self._set_limit(limited, 3)
        # Submit B's Other match first. Reissue would return it before the preferred pass.
        self.client_b.submit_result(other_held.id, "Player1Win")
        self.assertEqual(self._competition_id(self.client_b.post_to_matches()), limited.id)
        self.assertEqual(self._competition_id(self.client_c.post_to_matches()), limited.id)

        ac_d, client_d = self._new_ac("arenaclient-d")
        taken = self._match(client_d.post_to_matches())
        self.assertNotEqual(taken.round.competition_id, limited.id)
        self.assertEqual(taken.assigned_to_id, ac_d.id)

    def test_setting_a_limit_on_an_open_competition_keeps_the_earliest_claimers(self):
        # Seed Other with started matches first. Otherwise its empty recent share jumps it ahead of Open.
        other = self._make_comp("Other", bot_count=4, owner=self.staffUser1)
        for _ in range(3):
            self._finish(self.client_a, self.client_a.post_to_matches())
        comp = self._make_comp("Open", bot_count=6, limit=None)
        for client in (self.client_a, self.client_b, self.client_c):
            self._finish(client, client.post_to_matches())
        self._set_limit(comp, 1)
        self.assertEqual(self._competition_id(self.client_a.post_to_matches()), comp.id)
        self.assertEqual(self._competition_id(self.client_b.post_to_matches()), other.id)
        self.assertEqual(self._competition_id(self.client_c.post_to_matches()), other.id)

        # Finish the matches B and C already hold, then play the round out and pause it.
        self._submit_started(other)
        self._play_out(self.client_b, other)
        other.pause()
        self.assertEqual(self._competition_id(self.client_c.post_to_matches()), comp.id)
        self.assertEqual(self._competition_id(self.client_b.post_to_matches()), comp.id)

    def test_clearing_the_limit_lets_every_client_prefer_the_competition(self):
        limited = self._make_comp("Limited", bot_count=4, limit=1)
        self.client_a.post_to_matches()
        other = self._make_comp("Other", bot_count=2, owner=self.staffUser1)
        other_held = self._match(self.client_b.post_to_matches())
        self.assertEqual(other_held.round.competition_id, other.id)
        self._set_limit(limited, None)
        # Submit so the next poll is not a reissue of Other. Limited has more participants,
        # so the preferred pass serves it before Other's next round.
        self.client_b.submit_result(other_held.id, "Player1Win")
        self.assertEqual(self._competition_id(self.client_b.post_to_matches()), limited.id)

    def test_stale_preferred_client_yields_the_window(self):
        limited = self._make_comp("Limited", bot_count=4, limit=1)
        finished = self._match(self.client_a.post_to_matches())
        self.client_a.submit_result(finished.id, "Player1Win")
        self._age_result(Match.objects.get(id=finished.id))

        claimed = self._match(self.client_b.post_to_matches())
        self.assertEqual(claimed.assigned_to_id, self.ac_b.id)
        self.assertEqual(claimed.round.competition_id, limited.id)

        other = self._make_comp("Other", bot_count=2, owner=self.staffUser1)
        self.assertEqual(self._competition_id(self.client_a.post_to_matches()), other.id)

        self._finish(self.client_a, Match.objects.get(round__competition=other, result__isnull=True).id)
        other.pause()
        filled = self._match(self.client_a.post_to_matches())
        self.assertEqual(filled.round.competition_id, limited.id)
        self.assertEqual(filled.assigned_to_id, self.ac_a.id)

    def test_unfinished_match_keeps_a_client_preferred_past_the_timeout(self):
        limited = self._make_comp("Limited", bot_count=4, limit=1)
        held = self._match(self.client_a.post_to_matches())
        self.assertEqual(held.round.competition_id, limited.id)
        held.started = timezone.now() - (config.TIMEOUT_MATCHES_AFTER + timedelta(hours=1))
        held.save(update_fields=["started"])

        other = self._make_comp("Other", bot_count=2, owner=self.staffUser1)
        self.assertEqual(self._competition_id(self.client_b.post_to_matches()), other.id)
        again = self.client_a.post_to_matches()
        self.assertEqual(again.data["id"], held.id)

    def test_admin_form_round_trips_the_limit(self):
        comp = self._make_comp("Editable", bot_count=2)
        data = self._admin_data(comp)

        data["arena_client_limit"] = "2"
        form = CompetitionAdminForm(data, instance=comp)
        self.assertTrue(form.is_valid(), form.errors)
        form.save()
        comp.refresh_from_db()
        self.assertEqual(comp.arena_client_limit, 2)

        data["arena_client_limit"] = ""
        form = CompetitionAdminForm(data, instance=comp)
        self.assertTrue(form.is_valid(), form.errors)
        form.save()
        comp.refresh_from_db()
        self.assertIsNone(comp.arena_client_limit)

        comp.arena_client_limit = 2
        comp.save(update_fields=["arena_client_limit"])
        data["arena_client_limit"] = "0"
        form = CompetitionAdminForm(data, instance=comp)
        self.assertFalse(form.is_valid())
        self.assertIn("arena_client_limit", form.errors)
        comp.refresh_from_db()
        self.assertEqual(comp.arena_client_limit, 2)

    def _admin_data(self, comp: Competition) -> dict:
        form = CompetitionAdminForm(instance=comp)
        data = {}
        for name, field in form.fields.items():
            if name == "wiki_article_content":
                article = comp.get_wiki_article()
                revision = article.current_revision if article is not None else None
                data[name] = revision.content if revision is not None else ""
                continue
            value = form.initial.get(name)
            if isinstance(value, bool):
                if value:
                    data[name] = "on"
                continue
            if hasattr(value, "pk"):
                data[name] = value.pk
                continue
            if isinstance(value, Iterable) and not isinstance(value, (str, bytes)):
                data[name] = [item.pk if hasattr(item, "pk") else item for item in value]
                continue
            if hasattr(value, "strftime"):
                data[name] = value.strftime("%Y-%m-%d %H:%M:%S")
                continue
            data[name] = "" if value is None else value
        return data
