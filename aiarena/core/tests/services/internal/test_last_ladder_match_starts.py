from datetime import timedelta

from django.utils import timezone

import pytest

from aiarena.core.models import CompetitionParticipation, Match, MatchParticipation, Round
from aiarena.core.services.service_implementations import _matches
from aiarena.core.services.service_implementations._matches import _last_ladder_match_starts


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


def test_returns_most_recent_start_per_bot(make_bot, make_match):
    bot1, bot2 = make_bot("bot1"), make_bot("bot2")
    now = timezone.now()
    make_match(bot1, bot2, started=now - timedelta(hours=2))
    latest = now - timedelta(minutes=30)
    make_match(bot1, bot2, started=latest)

    assert _last_ladder_match_starts([bot1.id, bot2.id]) == {bot1.id: latest, bot2.id: latest}


def test_bot_that_has_never_played_is_absent(make_bot, make_match):
    """Absent bots fall back to datetime.min at the call site, i.e. are treated as
    maximally starved. They must not appear with a null or bogus value."""
    bot1, bot2 = make_bot("bot1"), make_bot("bot2")
    played = timezone.now() - timedelta(minutes=10)
    make_match(bot1, bot2, started=played)
    never_played = make_bot("never_played")

    assert _last_ladder_match_starts([bot1.id, never_played.id]) == {bot1.id: played}


def test_unstarted_matches_are_ignored(make_bot, make_match):
    bot1, bot2 = make_bot("bot1"), make_bot("bot2")
    make_match(bot1, bot2, started=None)

    assert _last_ladder_match_starts([bot1.id, bot2.id]) == {}


def test_matches_without_a_round_are_ignored(make_bot, make_match):
    """Requested (non-ladder) matches have no round and must not count, even
    though they have a start time."""
    bot1, bot2 = make_bot("bot1"), make_bot("bot2")
    ladder_start = timezone.now() - timedelta(hours=3)
    make_match(bot1, bot2, started=ladder_start)
    make_match(bot1, bot2, started=timezone.now(), in_round=False)

    assert _last_ladder_match_starts([bot1.id, bot2.id]) == {bot1.id: ladder_start, bot2.id: ladder_start}


def test_matches_outside_the_window_are_ignored(make_bot, make_match):
    """Bots idle for longer than the window are absent, same as never-played ones."""
    recent_bot, old_bot = make_bot("recent"), make_bot("old")
    now = timezone.now()
    recent_start = now - timedelta(minutes=5)
    make_match(recent_bot, recent_bot, started=recent_start)
    make_match(old_bot, old_bot, started=now - _matches._LAST_MATCH_WINDOW - timedelta(minutes=1))

    assert _last_ladder_match_starts([recent_bot.id, old_bot.id]) == {recent_bot.id: recent_start}


def test_start_time_exactly_on_the_window_boundary(make_bot, make_match, monkeypatch):
    bot1, bot2 = make_bot("bot1"), make_bot("bot2")
    now = timezone.now()
    boundary = now - _matches._LAST_MATCH_WINDOW
    make_match(bot1, bot2, started=boundary)
    monkeypatch.setattr(_matches.timezone, "now", lambda: now)

    assert _last_ladder_match_starts([bot1.id, bot2.id]) == {bot1.id: boundary, bot2.id: boundary}


def test_future_start_time_is_reported(make_bot, make_match):
    """The window has no upper bound, so a match started by a host with a skewed
    clock is still the bot's most recent start."""
    bot1, bot2 = make_bot("bot1"), make_bot("bot2")
    future = timezone.now() + timedelta(hours=2)
    make_match(bot1, bot2, started=future)

    assert _last_ladder_match_starts([bot1.id, bot2.id]) == {bot1.id: future, bot2.id: future}


def test_empty_input(db):
    assert _last_ladder_match_starts([]) == {}


def test_duplicate_and_unknown_bot_ids(make_bot, make_match):
    bot1, bot2 = make_bot("bot1"), make_bot("bot2")
    started = timezone.now() - timedelta(minutes=15)
    make_match(bot1, bot2, started=started)
    unknown_id = bot2.id + 10_000

    assert _last_ladder_match_starts([bot1.id, bot1.id, unknown_id]) == {bot1.id: started}


def test_single_query_even_with_idle_bots(make_bot, make_match, django_assert_num_queries):
    bot1, bot2 = make_bot("bot1"), make_bot("bot2")
    make_match(bot1, bot2, started=timezone.now() - timedelta(minutes=5))
    never_played = make_bot("never")

    with django_assert_num_queries(1):
        _last_ladder_match_starts([bot1.id, bot2.id, never_played.id])
