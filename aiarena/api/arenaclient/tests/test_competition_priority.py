from collections import Counter, deque
from collections.abc import Iterable
from datetime import timedelta

from django.conf import settings as django_settings
from django.core.cache import cache
from django.test import SimpleTestCase, TransactionTestCase, override_settings
from django.utils import timezone

from constance import config
from rest_framework.authtoken.models import Token

from aiarena import settings
from aiarena.api.arenaclient.common.ac_coordinator import (
    RECENT_MATCH_WINDOW,
    competition_priority_order,
    rank_competitions,
)
from aiarena.api.arenaclient.testing_utils import AcApiTestingClient
from aiarena.core.models import ArenaClient, Competition, Map, Match, Round
from aiarena.core.models.bot_race import BotRace
from aiarena.core.tests.test_mixins import LoggedInMixin
from aiarena.frontend.admin import CompetitionAdminForm


# A real cache backend, so a test that sees the order change proves nothing between calls is cached.
LOCMEM_CACHES = {
    **django_settings.CACHES,
    "default": {
        "BACKEND": "django.core.cache.backends.locmem.LocMemCache",
        "LOCATION": "competition-priority-tests",
    },
}


class RankCompetitionsTests(SimpleTestCase):
    def test_ranks_by_recent_matches_per_entitlement(self):
        entitlements = {1: 300, 2: 100}
        # Competition 1 holds 3 of 4 recent matches, exactly its share, so the ratios tie and the larger goes first.
        self.assertEqual(rank_competitions(entitlements, [1, 1, 1, 2]), [1, 2])
        # Competition 1 is over its share.
        self.assertEqual(rank_competitions(entitlements, [1, 1, 1, 1, 2]), [2, 1])
        # Competition 2 is over its share.
        self.assertEqual(rank_competitions(entitlements, [1, 1, 1, 2, 2]), [1, 2])

    def test_weight_changes_the_ranking(self):
        recent = [1, 2]
        self.assertEqual(rank_competitions({1: 100, 2: 100}, recent), [1, 2])
        self.assertEqual(rank_competitions({1: 100, 2: 200}, recent), [2, 1])

    def test_no_recent_matches_ranks_larger_entitlement_first(self):
        self.assertEqual(rank_competitions({1: 100, 2: 300, 3: 200}, []), [2, 3, 1])

    def test_full_tie_is_broken_by_id(self):
        self.assertEqual(rank_competitions({3: 100, 1: 100, 2: 100}, []), [1, 2, 3])

    def test_zero_entitlement_sorts_last_without_raising(self):
        self.assertEqual(rank_competitions({1: 0, 2: 100, 3: 50}, [2, 2, 2, 1]), [3, 2, 1])

    def test_zero_and_negative_entitlement_sort_last(self):
        self.assertEqual(rank_competitions({5: 0, 6: 100, 7: -3}, [6, 6, 6]), [6, 5, 7])

    def test_empty_inputs(self):
        self.assertEqual(rank_competitions({}, []), [])
        self.assertEqual(rank_competitions({}, [1, 2]), [])


class RankConvergenceTests(SimpleTestCase):
    """Reference games: repeatedly give the next match to the top-ranked playable competition."""

    def _play(self, entitlements, unplayable=(), picks=3000, window=100):
        recent = deque(maxlen=window)
        played = Counter()
        for _ in range(picks):
            order = rank_competitions(entitlements, list(recent))
            self.assertCountEqual(order, entitlements.keys())
            chosen = next(c for c in order if c not in unplayable)
            recent.append(chosen)
            played[chosen] += 1
        return played

    def test_converges_to_weight_ratio(self):
        played = self._play({1: 4 * 100, 2: 4 * 50})
        self.assertAlmostEqual(played[1] / played[2], 2.0, delta=0.05)

    def test_converges_to_participant_times_weight(self):
        played = self._play({1: 60 * 100, 2: 20 * 50, 3: 10 * 100})
        total = sum(played.values())
        for cid, ent in {1: 6000, 2: 1000, 3: 1000}.items():
            self.assertAlmostEqual(played[cid] / total, ent / 8000, delta=0.01)

    def test_unplayable_competition_does_not_distort_the_rest(self):
        with_p = self._play({1: 6000, 2: 1000, 9: 6000}, unplayable={9})
        without = self._play({1: 6000, 2: 1000})
        self.assertEqual(with_p, without)
        # Shares are whole matches in a 100-match window, so they land within about one match of 6000:1000.
        self.assertAlmostEqual(with_p[2] / sum(with_p.values()), 1 / 7, delta=1 / 100)

    def test_share_floors_at_one_match_per_window(self):
        """A competition with no match in the window ranks first, so no positive weight goes below ~1/window."""
        played = self._play({1: 100 * 100, 2: 1 * 1}, picks=20000)
        self.assertAlmostEqual(played[2] / 20000, 1 / 101, delta=0.001)


@override_settings(CACHES=LOCMEM_CACHES)
class SchedulingTestCase(LoggedInMixin, TransactionTestCase):
    """Shared fixtures. Runs with a real cache backend so nothing can hide behind a missing cache."""

    def setUp(self):
        super().setUp()
        cache.clear()
        self.addCleanup(cache.clear)
        settings.MAX_USER_BOT_PARTICIPATIONS_ACTIVE_FREE_TIER = 60
        config.MAX_USER_BOT_COUNT = 60
        config.REISSUE_UNFINISHED_MATCHES = False
        self.test_client.login(self.staffUser1)
        game = self.test_client.create_game("StarCraft II", ".SC2Map")
        self.game_mode = self.test_client.create_gamemode("Melee", game.id)
        BotRace.create_all_races()
        self._bot_seq = 0

    def _make_comp(self, name, bots, trusted=True, downloadable=False) -> Competition:
        comp = self.test_client.create_competition(name, self.game_mode.id, require_trusted_infrastructure=trusted)
        self.test_client.open_competition(comp.id)
        comp.refresh_from_db()
        # open_competition posts a partial admin form, which resets the trust flag.
        comp.require_trusted_infrastructure = trusted
        comp.save(update_fields=["require_trusted_infrastructure"])
        self._create_map_for_competition(f"map-{name}", comp.id)
        races = [BotRace.terran(), BotRace.zerg(), BotRace.protoss(), BotRace.random()]
        for index in range(bots):
            self._bot_seq += 1
            self._create_active_bot_for_competition(
                comp.id,
                self.regularUser1,
                f"{name}-bot{self._bot_seq}",
                races[index % len(races)],
                downloadable=downloadable,
            )
        comp.refresh_from_db()
        return comp

    def _add_history(self, comp: Competition, count: int, minutes_ago: int = 30):
        """Add ``count`` started ladder matches to a completed round of ``comp``, so new rounds can still be generated."""
        round_ = Round.objects.create(
            competition=comp,
            number=Round.objects.filter(competition=comp).count() + 1,
            complete=True,
            finished=timezone.now(),
        )
        map_ = Map.objects.filter(competitions=comp).first()
        start = timezone.now() - timedelta(minutes=minutes_ago)
        Match.objects.bulk_create(
            [Match(round=round_, map=map_, started=start + timedelta(seconds=i)) for i in range(count)]
        )

    def _add_requested_matches(self, comp: Competition, count: int, minutes_ago: int):
        """Started matches requested by a user. They belong to no round, so are not ladder matches."""
        map_ = Map.objects.filter(competitions=comp).first()
        start = timezone.now() - timedelta(minutes=minutes_ago)
        Match.objects.bulk_create(
            [
                Match(round=None, map=map_, started=start + timedelta(seconds=i), requested_by=self.regularUser1)
                for i in range(count)
            ]
        )

    def _set_weight(self, comp: Competition, weight):
        Competition.objects.filter(id=comp.id).update(scheduling_weight=weight)

    def _set_status(self, comp: Competition, status: str):
        Competition.objects.filter(id=comp.id).update(status=status)

    def _new_ac(self, username, trusted=True) -> AcApiTestingClient:
        ac = ArenaClient.objects.create(
            username=username,
            email=f"{username}@dev.aiarena.net",
            type="ARENA_CLIENT",
            trusted=trusted,
            owner=self.staffUser1,
        )
        return AcApiTestingClient(api_token=Token.objects.create(user=ac).key)

    def _competition_id(self, response) -> int:
        self.assertEqual(response.status_code, 201, getattr(response, "data", response))
        return Match.objects.select_related("round").get(id=response.data["id"]).round.competition_id


class CompetitionPriorityOrderTests(SchedulingTestCase):
    def test_order_reflects_active_participants_times_weight(self):
        big = self._make_comp("Big", bots=3)
        small = self._make_comp("Small", bots=2)
        self.assertEqual(competition_priority_order(), [big.id, small.id])

        self._set_weight(small, 200)
        self.assertEqual(competition_priority_order(), [small.id, big.id])

        self._set_weight(small, 50)
        self.assertEqual(competition_priority_order(), [big.id, small.id])

    def test_null_weight_is_treated_as_the_default(self):
        big = self._make_comp("Big", bots=3)
        small = self._make_comp("Small", bots=2)
        # Entitlements: big 3 x 100 = 300 when NULL, small 2 x 140 = 280.
        self._set_weight(big, None)
        self._set_weight(small, 140)
        self.assertEqual(competition_priority_order(), [big.id, small.id])

        # Had NULL counted as less than 100, or as zero, big would not stay first against 2 x 160 = 320.
        self._set_weight(small, 160)
        self.assertEqual(competition_priority_order(), [small.id, big.id])

    def test_zero_weight_sorts_last_without_crashing(self):
        zero = self._make_comp("Zero", bots=4)
        other = self._make_comp("Other", bots=2)
        self._add_history(other, 50)
        self._set_weight(zero, 0)
        self.assertEqual(competition_priority_order(), [other.id, zero.id])

    def test_only_active_participations_count(self):
        mostly_inactive = self._make_comp("MostlyInactive", bots=3)
        two_bots = self._make_comp("TwoBots", bots=2)
        for participation in mostly_inactive.participations.all()[:2]:
            participation.active = False
            participation.save()
        # Entitlements: 1 active x 100 = 100 against 2 x 100 = 200. Counting all three would reverse this.
        self.assertEqual(competition_priority_order(), [two_bots.id, mostly_inactive.id])

    def test_unschedulable_competitions_are_excluded(self):
        open_comp = self._make_comp("Open", bots=2)
        paused = self._make_comp("Paused", bots=2)
        closing = self._make_comp("Closing", bots=2)
        frozen = self._make_comp("Frozen", bots=2)
        self._set_status(paused, "paused")
        self._set_status(closing, "closing")
        self._set_status(frozen, "frozen")
        self.assertEqual(competition_priority_order(), [open_comp.id, paused.id, closing.id])

    def test_competitions_without_active_participations_are_excluded(self):
        with_bots = self._make_comp("WithBots", bots=2)
        self._make_comp("Empty", bots=0)
        inactive = self._make_comp("Inactive", bots=2)
        inactive.participations.update(active=False)
        self.assertEqual(competition_priority_order(), [with_bots.id])

    def test_requested_matches_do_not_take_window_slots(self):
        big = self._make_comp("Big", bots=3)
        small = self._make_comp("Small", bots=2)
        self._add_history(big, 30, minutes_ago=40)
        self._add_requested_matches(big, RECENT_MATCH_WINDOW, minutes_ago=5)
        # Had the newer requested matches taken window slots, big's history would be evicted and big would rank first.
        self.assertEqual(competition_priority_order(), [small.id, big.id])

    def test_matches_of_unschedulable_competitions_do_not_take_window_slots(self):
        big = self._make_comp("Big", bots=3)
        small = self._make_comp("Small", bots=2)
        frozen = self._make_comp("Frozen", bots=2)
        self._add_history(big, 30, minutes_ago=40)
        self._add_history(frozen, RECENT_MATCH_WINDOW, minutes_ago=5)
        self._set_status(frozen, "frozen")
        self.assertEqual(competition_priority_order(), [small.id, big.id])

    def test_window_holds_exactly_the_latest_recent_match_window_matches(self):
        self.assertEqual(RECENT_MATCH_WINDOW % 2, 0)
        half = RECENT_MATCH_WINDOW // 2
        first = self._make_comp("First", bots=4)
        second = self._make_comp("Second", bots=4)
        self._add_history(first, 1, minutes_ago=60)  # just outside the window
        self._add_history(first, half, minutes_ago=30)
        self._add_history(second, half, minutes_ago=20)
        # Inside the window the two are exactly tied, so the lower id goes first. A window one match larger would
        # give first an extra match and put second ahead.
        self.assertEqual(competition_priority_order(), [first.id, second.id])

    def test_order_changes_immediately_after_a_ladder_match_starts(self):
        big = self._make_comp("Big", bots=3)
        small = self._make_comp("Small", bots=2)
        self.assertEqual(competition_priority_order(), [big.id, small.id])

        self._add_history(big, 1, minutes_ago=0)
        self.assertEqual(competition_priority_order(), [small.id, big.id])

    def test_order_changes_immediately_after_a_status_change(self):
        big = self._make_comp("Big", bots=3)
        small = self._make_comp("Small", bots=2)
        self.assertEqual(competition_priority_order(), [big.id, small.id])

        self._set_status(big, "frozen")
        self.assertEqual(competition_priority_order(), [small.id])

    def test_order_changes_immediately_after_a_weight_change(self):
        big = self._make_comp("Big", bots=3)
        small = self._make_comp("Small", bots=2)
        self.assertEqual(competition_priority_order(), [big.id, small.id])

        self._set_weight(small, 1000)
        self.assertEqual(competition_priority_order(), [small.id, big.id])


class CoordinatorSchedulingTests(SchedulingTestCase):
    def test_weight_overrides_recent_match_counts(self):
        heavy = self._make_comp("Heavy", bots=4)
        light = self._make_comp("Light", bots=4)
        self._add_history(heavy, 12)
        self._add_history(light, 10)
        self._set_weight(heavy, 100)
        self._set_weight(light, 50)
        # Counts alone would pick light (10 < 12), but heavy is entitled to twice the share: 12/400 < 10/200.
        self.assertEqual(self._competition_id(self.test_ac_api_client.post_to_matches()), heavy.id)

    def test_client_follows_a_weight_change(self):
        big = self._make_comp("Big", bots=4)
        small = self._make_comp("Small", bots=2)
        self._add_history(big, 10)
        self._add_history(small, 10)
        self.assertEqual(competition_priority_order()[0], big.id)
        self.assertEqual(self._competition_id(self.test_ac_api_client.post_to_matches()), big.id)
        # Big is still due after that match: 11/400 against 10/200.
        self.assertEqual(competition_priority_order()[0], big.id)

        self._set_weight(small, 1000)
        self.assertEqual(self._competition_id(self._new_ac("arenaclient-2").post_to_matches()), small.id)

    def test_second_client_sees_the_first_clients_match(self):
        a = self._make_comp("A", bots=5)
        b = self._make_comp("B", bots=4)
        first = self._competition_id(self.test_ac_api_client.post_to_matches())
        self.assertEqual(first, a.id)  # no history: larger competition first
        second = self._competition_id(self._new_ac("arenaclient-2").post_to_matches())
        self.assertEqual(second, b.id)

    def test_unplayable_competition_does_not_flip_the_choice(self):
        """A paused competition full of bots must not make the over-served competition win.

        A has 6 bots and 29 of the last 40 matches (below its fair 30), B has 2 bots and 11 (above its fair 10),
        so A is due. A formula of recent share minus participant share diluted both targets with P's 8 bots and
        picked B.
        """
        a = self._make_comp("A", bots=6)
        b = self._make_comp("B", bots=2)
        paused = self._make_comp("P", bots=8)
        paused.pause()
        self._add_history(a, 29)
        self._add_history(b, 11)
        self.assertEqual(self._competition_id(self.test_ac_api_client.post_to_matches()), a.id)

    def test_zero_weight_competition_still_fills_in(self):
        only = self._make_comp("Only", bots=4)
        self._set_weight(only, 0)
        self.assertEqual(self._competition_id(self.test_ac_api_client.post_to_matches()), only.id)

    def test_zero_weight_yields_to_any_positive_weight(self):
        zero = self._make_comp("Zero", bots=4)
        positive = self._make_comp("Positive", bots=4)
        self._add_history(positive, 50)
        self._set_weight(zero, 0)
        self.assertEqual(self._competition_id(self.test_ac_api_client.post_to_matches()), positive.id)

    def test_single_bot_competition_ranked_first_is_skipped(self):
        lonely = self._make_comp("Lonely", bots=1)
        other = self._make_comp("Other", bots=4)
        self._add_history(other, 20)
        self.assertEqual(competition_priority_order()[0], lonely.id)
        self.assertEqual(self._competition_id(self.test_ac_api_client.post_to_matches()), other.id)
        self.assertFalse(Round.objects.filter(competition=lonely).exists())

    def test_closing_competition_ranked_first_falls_through_without_creating_a_round(self):
        closing = self._make_comp("Closing", bots=4)
        other = self._make_comp("Other", bots=2)
        self._set_status(closing, "closing")
        # Closing has no round to play and may not generate a new one.
        self.assertEqual(competition_priority_order()[0], closing.id)
        self.assertEqual(self._competition_id(self.test_ac_api_client.post_to_matches()), other.id)
        self.assertFalse(Round.objects.filter(competition=closing).exists())

    def test_untrusted_client_skips_competitions_requiring_trusted_infrastructure(self):
        trusted_only = self._make_comp("TrustedOnly", bots=4, trusted=True)
        # Untrusted clients may only run publicly downloadable bots.
        public = self._make_comp("Public", bots=2, trusted=False, downloadable=True)
        self.assertEqual(competition_priority_order()[0], trusted_only.id)
        untrusted = self._new_ac("untrusted-ac", trusted=False)
        self.assertEqual(self._competition_id(untrusted.post_to_matches()), public.id)
        self.assertFalse(Match.objects.filter(round__competition=trusted_only, started__isnull=False).exists())


class CompetitionSchedulingWeightAdminTests(LoggedInMixin, TransactionTestCase):
    def setUp(self):
        super().setUp()
        self.test_client.login(self.staffUser1)
        game = self.test_client.create_game("StarCraft II", ".SC2Map")
        game_mode = self.test_client.create_gamemode("Melee", game.id)
        self.comp = self.test_client.create_competition("Editable", game_mode.id)

    def _admin_data(self) -> dict:
        form = CompetitionAdminForm(instance=self.comp)
        data = {}
        for name in form.fields:
            if name == "wiki_article_content":
                data[name] = self.comp.get_wiki_article().current_revision.content
                continue
            value = form.initial.get(name)
            if isinstance(value, bool):
                if value:
                    data[name] = "on"
            elif hasattr(value, "pk"):
                data[name] = value.pk
            elif isinstance(value, Iterable) and not isinstance(value, (str, bytes)):
                data[name] = [item.pk if hasattr(item, "pk") else item for item in value]
            elif hasattr(value, "strftime"):
                data[name] = value.strftime("%Y-%m-%d %H:%M:%S")
            else:
                data[name] = "" if value is None else value
        return data

    def test_new_competition_gets_the_default_weight(self):
        self.assertEqual(self.comp.scheduling_weight, Competition.DEFAULT_SCHEDULING_WEIGHT)

    def test_form_rejects_zero(self):
        data = self._admin_data()
        data["scheduling_weight"] = "0"
        form = CompetitionAdminForm(data, instance=self.comp)
        self.assertFalse(form.is_valid())
        self.assertIn("scheduling_weight", form.errors)

    def test_form_accepts_a_blank_value(self):
        data = self._admin_data()
        data["scheduling_weight"] = ""
        form = CompetitionAdminForm(data, instance=self.comp)
        self.assertTrue(form.is_valid(), form.errors)
        form.save()
        self.comp.refresh_from_db()
        self.assertIsNone(self.comp.scheduling_weight)

    def test_partial_admin_post_keeps_the_stored_weight(self):
        Competition.objects.filter(id=self.comp.id).update(scheduling_weight=50)
        self.test_client.open_competition(self.comp.id)  # posts a form that omits scheduling_weight
        self.comp.refresh_from_db()
        self.assertEqual(self.comp.scheduling_weight, 50)
