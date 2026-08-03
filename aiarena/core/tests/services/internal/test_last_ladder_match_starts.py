"""Equivalence tests for the windowed last-ladder-match-start lookup.

`_last_ladder_match_starts` replaced a single, obviously-correct query with one
that narrows its search to a widening time window. Every scenario below therefore
runs against *both* implementations, so that agreement between them is a
structural property of the suite rather than something each test has to remember
to assert.

The query-count tests at the bottom are deliberately not parametrized -- they pin
the behaviour that motivated the change, which only the new implementation has.
"""

from datetime import UTC, datetime, timedelta

from django.db.models import Max
from django.utils import timezone

import pytest

from aiarena.core.models import CompetitionParticipation, Match, MatchParticipation, Round
from aiarena.core.services.service_implementations import _matches
from aiarena.core.services.service_implementations._matches import _last_ladder_match_starts


def _reference_query(bot_ids):
    """The query this helper replaced, kept verbatim as the oracle.

    Obviously correct and obviously too slow: the round/started filters exclude
    almost nothing, so it scans both tables in full.
    """
    return dict(
        MatchParticipation.objects.filter(
            bot_id__in=bot_ids,
            match__round__isnull=False,
            match__started__isnull=False,
        )
        .values("bot_id")
        .annotate(last_start=Max("match__started"))
        .values_list("bot_id", "last_start")
    )


@pytest.fixture
def make_bot(db, user, competition, all_bot_races, bot_factory):
    """Bots that are participants in the competition under test."""

    def _make_bot(name):
        bot = bot_factory(user=user, name=name)
        CompetitionParticipation.objects.create(competition=competition, bot=bot)
        return bot

    return _make_bot


@pytest.fixture
def round_(db, competition):
    return Round.objects.create(competition=competition)


@pytest.fixture
def make_match(db, map, round_):
    def _make_match(bot1, bot2, started=None, in_round=True):
        match = Match.objects.create(map=map, round=round_ if in_round else None, started=started)
        MatchParticipation.objects.create(match=match, participant_number=1, bot=bot1)
        MatchParticipation.objects.create(match=match, participant_number=2, bot=bot2)
        return match

    return _make_match


@pytest.mark.parametrize("last_ladder_match_starts", [_reference_query, _last_ladder_match_starts])
def test_returns_most_recent_start_per_bot(last_ladder_match_starts, make_bot, make_match):
    bot1, bot2 = make_bot("bot1"), make_bot("bot2")
    now = timezone.now()
    make_match(bot1, bot2, started=now - timedelta(hours=2))
    latest = now - timedelta(minutes=30)
    make_match(bot1, bot2, started=latest)

    assert last_ladder_match_starts([bot1.id, bot2.id]) == {bot1.id: latest, bot2.id: latest}


@pytest.mark.parametrize("last_ladder_match_starts", [_reference_query, _last_ladder_match_starts])
def test_bot_that_has_never_played_is_absent(last_ladder_match_starts, make_bot, make_match):
    """Absent bots fall back to datetime.min at the call site, i.e. are treated as
    maximally starved. They must not appear with a null or bogus value."""
    bot1, bot2 = make_bot("bot1"), make_bot("bot2")
    played = timezone.now() - timedelta(minutes=10)
    make_match(bot1, bot2, started=played)
    never_played = make_bot("never_played")

    assert last_ladder_match_starts([bot1.id, never_played.id]) == {bot1.id: played}


@pytest.mark.parametrize("last_ladder_match_starts", [_reference_query, _last_ladder_match_starts])
def test_unstarted_matches_are_ignored(last_ladder_match_starts, make_bot, make_match):
    bot1, bot2 = make_bot("bot1"), make_bot("bot2")
    make_match(bot1, bot2, started=None)

    assert last_ladder_match_starts([bot1.id, bot2.id]) == {}


@pytest.mark.parametrize("last_ladder_match_starts", [_reference_query, _last_ladder_match_starts])
def test_matches_without_a_round_are_ignored(last_ladder_match_starts, make_bot, make_match):
    """Requested (non-ladder) matches have no round and must not count, even
    though they have a start time."""
    bot1, bot2 = make_bot("bot1"), make_bot("bot2")
    ladder_start = timezone.now() - timedelta(hours=3)
    make_match(bot1, bot2, started=ladder_start)
    make_match(bot1, bot2, started=timezone.now(), in_round=False)

    assert last_ladder_match_starts([bot1.id, bot2.id]) == {bot1.id: ladder_start, bot2.id: ladder_start}


@pytest.mark.parametrize("last_ladder_match_starts", [_reference_query, _last_ladder_match_starts])
def test_only_non_ladder_matches_means_absent(last_ladder_match_starts, make_bot, make_match):
    bot1, bot2 = make_bot("bot1"), make_bot("bot2")
    make_match(bot1, bot2, started=timezone.now(), in_round=False)

    assert last_ladder_match_starts([bot1.id, bot2.id]) == {}


@pytest.mark.parametrize("last_ladder_match_starts", [_reference_query, _last_ladder_match_starts])
def test_match_older_than_every_window_is_still_found(last_ladder_match_starts, make_bot, make_match):
    """Widening stops once the window predates the arena, and that final pass drops
    the filter entirely rather than clamping at the epoch -- so a match older than
    _ARENA_EPOCH must still be reported exactly."""
    bot1, bot2 = make_bot("bot1"), make_bot("bot2")
    ancient = datetime(2015, 6, 1, tzinfo=UTC)
    make_match(bot1, bot2, started=ancient)

    assert last_ladder_match_starts([bot1.id, bot2.id]) == {bot1.id: ancient, bot2.id: ancient}


@pytest.mark.parametrize("last_ladder_match_starts", [_reference_query, _last_ladder_match_starts])
def test_match_just_outside_the_first_window_is_found(last_ladder_match_starts, make_bot, make_match):
    """A bot missing from a window proves the window was too narrow; widening must
    find it rather than reporting it as never having played."""
    bot1, bot2 = make_bot("bot1"), make_bot("bot2")
    # Far enough back that several widening steps are needed to reach it.
    started = timezone.now() - (_matches._LAST_MATCH_WINDOW_START * _matches._LAST_MATCH_WINDOW_GROWTH**2)
    make_match(bot1, bot2, started=started)

    assert last_ladder_match_starts([bot1.id, bot2.id]) == {bot1.id: started, bot2.id: started}


@pytest.mark.parametrize("last_ladder_match_starts", [_reference_query, _last_ladder_match_starts])
def test_widened_pass_still_reports_the_true_maximum(last_ladder_match_starts, make_bot, make_match):
    """Once a widened window does reach a bot, it sees several of that bot's matches
    at once and must report the most recent, not merely the first one found."""
    bot1, bot2 = make_bot("bot1"), make_bot("bot2")
    now = timezone.now()
    step = _matches._LAST_MATCH_WINDOW_START * _matches._LAST_MATCH_WINDOW_GROWTH
    make_match(bot1, bot2, started=now - step * 4)
    latest = now - step * 2
    make_match(bot1, bot2, started=latest)
    make_match(bot1, bot2, started=now - step * 3)

    assert last_ladder_match_starts([bot1.id, bot2.id]) == {bot1.id: latest, bot2.id: latest}


@pytest.mark.parametrize("last_ladder_match_starts", [_reference_query, _last_ladder_match_starts])
def test_start_time_exactly_on_the_window_boundary(last_ladder_match_starts, make_bot, make_match, monkeypatch):
    """The cutoff is inclusive, but even were it not the bot would be picked up by
    the next pass -- either way the value must be exact."""
    bot1, bot2 = make_bot("bot1"), make_bot("bot2")
    now = timezone.now()
    boundary = now - _matches._LAST_MATCH_WINDOW_START
    make_match(bot1, bot2, started=boundary)
    monkeypatch.setattr(_matches.timezone, "now", lambda: now)

    assert last_ladder_match_starts([bot1.id, bot2.id]) == {bot1.id: boundary, bot2.id: boundary}


@pytest.mark.parametrize("last_ladder_match_starts", [_reference_query, _last_ladder_match_starts])
def test_bots_resolved_across_different_passes(last_ladder_match_starts, make_bot, make_match):
    """A recent bot, a long-idle bot and a never-played bot together exercise every
    branch of the widening loop in one call."""
    recent_bot, old_bot, never_played = make_bot("recent"), make_bot("old"), make_bot("never")
    now = timezone.now()
    recent_start, old_start = now - timedelta(minutes=5), now - timedelta(days=300)
    make_match(recent_bot, recent_bot, started=recent_start)
    make_match(old_bot, old_bot, started=old_start)

    result = last_ladder_match_starts([recent_bot.id, old_bot.id, never_played.id])

    assert result == {recent_bot.id: recent_start, old_bot.id: old_start}


@pytest.mark.parametrize("last_ladder_match_starts", [_reference_query, _last_ladder_match_starts])
def test_future_start_time_is_reported(last_ladder_match_starts, make_bot, make_match):
    """The window has no upper bound, so a match started by a host with a skewed
    clock is still the bot's most recent start."""
    bot1, bot2 = make_bot("bot1"), make_bot("bot2")
    future = timezone.now() + timedelta(hours=2)
    make_match(bot1, bot2, started=future)

    assert last_ladder_match_starts([bot1.id, bot2.id]) == {bot1.id: future, bot2.id: future}


@pytest.mark.parametrize("last_ladder_match_starts", [_reference_query, _last_ladder_match_starts])
def test_empty_input(last_ladder_match_starts):
    assert last_ladder_match_starts([]) == {}


@pytest.mark.parametrize("last_ladder_match_starts", [_reference_query, _last_ladder_match_starts])
def test_duplicate_and_unknown_bot_ids(last_ladder_match_starts, make_bot, make_match):
    bot1, bot2 = make_bot("bot1"), make_bot("bot2")
    started = timezone.now() - timedelta(minutes=15)
    make_match(bot1, bot2, started=started)
    unknown_id = bot2.id + 10_000

    assert last_ladder_match_starts([bot1.id, bot1.id, unknown_id]) == {bot1.id: started}


@pytest.mark.parametrize("last_ladder_match_starts", [_reference_query, _last_ladder_match_starts])
def test_clock_before_the_arena_epoch(last_ladder_match_starts, make_bot, make_match, monkeypatch):
    """A frozen or skewed clock predating the arena makes the very first pass
    unbounded. It must stay exact rather than widen forever."""
    bot1, bot2 = make_bot("bot1"), make_bot("bot2")
    started = datetime(2017, 3, 1, tzinfo=UTC)
    make_match(bot1, bot2, started=started)
    monkeypatch.setattr(_matches.timezone, "now", lambda: datetime(2018, 6, 1, tzinfo=UTC))

    assert last_ladder_match_starts([bot1.id, bot2.id]) == {bot1.id: started, bot2.id: started}


# The remaining tests pin the cost of the new implementation, which is the reason
# it exists, so they deliberately run against it alone.


def test_recent_bots_resolve_in_a_single_query(make_bot, make_match, django_assert_num_queries):
    bot1, bot2 = make_bot("bot1"), make_bot("bot2")
    make_match(bot1, bot2, started=timezone.now() - timedelta(minutes=5))

    with django_assert_num_queries(1):
        _last_ladder_match_starts([bot1.id, bot2.id])


def test_never_played_bot_does_not_step_through_every_window(make_bot, make_match, django_assert_num_queries):
    """A bot that has never played would otherwise drag the loop through every
    widening step; a fruitless pass jumps straight to the exact one instead."""
    bot1, bot2 = make_bot("bot1"), make_bot("bot2")
    make_match(bot1, bot2, started=timezone.now() - timedelta(minutes=5))
    never_played = make_bot("never")

    with django_assert_num_queries(3):
        _last_ladder_match_starts([bot1.id, bot2.id, never_played.id])


def test_clock_before_epoch_costs_one_query(make_bot, make_match, monkeypatch, django_assert_num_queries):
    bot1, bot2 = make_bot("bot1"), make_bot("bot2")
    make_match(bot1, bot2, started=datetime(2017, 3, 1, tzinfo=UTC))
    monkeypatch.setattr(_matches.timezone, "now", lambda: datetime(2018, 6, 1, tzinfo=UTC))

    with django_assert_num_queries(1):
        _last_ladder_match_starts([bot1.id, bot2.id])
