from datetime import UTC, date, datetime, time, timedelta
from unittest import mock

import pytest

from aiarena.core.models import Competition, CompetitionSchedule, Round
from aiarena.core.services.service_implementations.internal.competition_scheduler import (
    process_competition_schedules,
)


NOON = time(12, 0)
SIM_START = datetime(2027, 1, 1, 12, tzinfo=UTC)
SIM_DAYS = 700  # 2027-01-01 .. 2028-11-30


@pytest.fixture
def make_schedule(game_mode):
    def _make_schedule(name, start, end, **kwargs):
        (start_month, start_day), (end_month, end_day) = start, end
        return CompetitionSchedule.objects.create(
            name=name,
            game_mode=game_mode,
            start_month=start_month,
            start_day=start_day,
            start_time=NOON,
            end_month=end_month,
            end_day=end_day,
            end_time=NOON,
            **kwargs,
        )

    return _make_schedule


def tick(now):
    """Run one scheduler pass as if the wall clock read `now`.

    Ticks land at 12:00, the same time schedules start and end, so a competition
    opens and starts closing on the tick of its scheduled day.
    """
    with mock.patch("django.utils.timezone.now", return_value=now):
        process_competition_schedules()


def simulate(days, start=SIM_START, step=timedelta(days=1), on_tick=None):
    now = start
    for _ in range(days):
        tick(now)
        if on_tick:
            on_tick(now)
        now += step


def timeline():
    """{name: (opened, closed, status)} for every scheduled competition."""
    result = {}
    for c in Competition.objects.filter(schedule__isnull=False).order_by("scheduled_start"):
        result[c.name] = (
            c.date_opened.date() if c.date_opened else None,
            c.date_closed.date() if c.date_closed else None,
            c.status,
        )
    return result


def print_timeline():
    print(f"\n{'competition':<42} {'opened':<12} {'closed':<12} status")
    for name, (opened, closed, status) in timeline().items():
        print(f"{name:<42} {opened!s:<12} {closed!s:<12} {status}")


MICRO = "TEST Sc2 AI Arena Micro Ladder {year}"
LADDER = "TEST Sc2 AI Arena {year}"

# (name, start (month, day), end (month, day), end day after clamping)
# Day values past the end of the month clamp to its last day (Jun 31 -> 30, Dec 32 -> 31).
SCHEDULES = [
    # Micro ladder: one tournament per quarter, overlapping the main ladder.
    (f"{MICRO} Q1", (1, 1), (3, 31), (3, 31)),
    (f"{MICRO} Q2", (4, 1), (6, 31), (6, 30)),
    (f"{MICRO} Q3", (7, 1), (9, 31), (9, 30)),
    (f"{MICRO} Q4", (10, 1), (12, 32), (12, 31)),
    # Main ladder, each quarter: a 1-month pre-season that hands over at 12:00 on the
    # 1st to a 2-month season.
    (f"{LADDER} Pre-Season 1", (1, 1), (2, 1), (2, 1)),
    (f"{LADDER} Season 1", (2, 1), (3, 31), (3, 31)),
    (f"{LADDER} Pre-Season 2", (4, 1), (5, 1), (5, 1)),
    (f"{LADDER} Season 2", (5, 1), (6, 31), (6, 30)),
    (f"{LADDER} Pre-Season 3", (7, 1), (8, 1), (8, 1)),
    (f"{LADDER} Season 3", (8, 1), (9, 31), (9, 30)),
    (f"{LADDER} Pre-Season 4", (10, 1), (11, 1), (11, 1)),
    (f"{LADDER} Season 4", (11, 1), (12, 32), (12, 31)),
]


def expected_timeline(years, sim_end):
    """What every schedule should have produced by `sim_end`, worked out independently."""
    expected = {}
    for year in years:
        for name, (start_month, start_day), _, (end_month, end_day) in SCHEDULES:
            opened = date(year, start_month, start_day)
            closed = date(year, end_month, end_day)
            if opened > sim_end:
                continue
            if closed > sim_end:
                expected[name.format(year=year)] = (opened, None, "open")
            else:
                expected[name.format(year=year)] = (opened, closed, "closed")
    return expected


def test_700_day_simulation(make_schedule):
    for name, start, end, _ in SCHEDULES:
        make_schedule(name, start=start, end=end)
    make_schedule("TEST Disabled {year}", start=(1, 1), end=(12, 31), enabled=False)

    simulate(SIM_DAYS)
    print_timeline()

    sim_end = (SIM_START + timedelta(days=SIM_DAYS - 1)).date()
    expected = expected_timeline([2027, 2028], sim_end)
    # Every schedule has started in both years; 2028 is cut off on Nov 30 with only the
    # entries ending Dec 31 still open.
    assert len(expected) == 2 * len(SCHEDULES)
    assert {name for name, (_, _, status) in expected.items() if status == "open"} == {
        "TEST Sc2 AI Arena Micro Ladder 2028 Q4",
        "TEST Sc2 AI Arena 2028 Season 4",
    }
    assert timeline() == expected


def test_hourly_ticks_create_each_competition_once(make_schedule):
    make_schedule(f"{LADDER} Season 1", start=(2, 1), end=(4, 31))

    simulate(24 * 3, start=datetime(2027, 1, 31, 22, tzinfo=UTC), step=timedelta(hours=1))

    assert Competition.objects.filter(schedule__isnull=False).count() == 1


def test_incomplete_round_holds_competition_in_closing(make_schedule):
    make_schedule(f"{LADDER} Season 1", start=(2, 1), end=(4, 31))
    simulate(1, start=datetime(2027, 2, 1, 12, tzinfo=UTC))
    competition = Competition.objects.get(name="TEST Sc2 AI Arena 2027 Season 1")
    round_ = Round.objects.create(competition=competition, complete=False)

    simulate(3, start=datetime(2027, 4, 30, 12, tzinfo=UTC))
    competition.refresh_from_db()
    assert competition.status == "closing"

    round_.complete = True
    round_.save()
    simulate(1, start=datetime(2027, 5, 3, 12, tzinfo=UTC))
    competition.refresh_from_db()
    assert competition.status == "closed"
    assert competition.date_closed.date() == date(2027, 5, 3)
