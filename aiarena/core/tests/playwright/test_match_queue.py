from django.utils import timezone

import pytest
from playwright.sync_api import Page, expect

from aiarena.core.models import Match, MatchParticipation, Round

from ..base import BrowserHelper


pytestmark = [pytest.mark.playwright]


def _match(bot, other_bot, map, **fields):
    match = Match.objects.create(map=map, **fields)
    MatchParticipation.objects.create(match=match, participant_number=1, bot=bot)
    MatchParticipation.objects.create(match=match, participant_number=2, bot=other_bot)
    return match


def test_match_queue_page(page: Page, bh: BrowserHelper, competition, bot, other_bot, map, arenaclient_user):
    requested = _match(bot, other_bot, map, started=timezone.now(), assigned_to=arenaclient_user)
    round = Round.objects.create(competition=competition)
    in_round = _match(bot, other_bot, map, round=round)

    page.goto(bh.reverse("match_queue"))

    expect(page.get_by_text("2 matches waiting: 1 running, 1 queued")).to_be_visible()
    expect(page.get_by_role("heading", name="Requested matches")).to_be_visible()
    expect(page.get_by_role("heading", name=f"Round {round.number} · {competition.name}")).to_be_visible()

    requested_row = page.get_by_role("row").filter(has_text=str(requested.id)).filter(has_text="ac1")
    expect(requested_row).to_contain_text(bot.name)
    expect(requested_row).to_contain_text(other_bot.name)
    expect(requested_row).to_contain_text(map.name)

    in_round_row = page.get_by_role("row").filter(has_text=str(in_round.id)).filter(has_text="Queued")
    expect(in_round_row).to_be_visible()

    # Filtering by the arena client's name leaves only the match assigned to it.
    page.get_by_placeholder("Filter by bot, map, client or match ID...").fill("ac1")
    expect(requested_row).to_be_visible()
    expect(in_round_row).to_have_count(0)
    # The round has nothing left that matches, so its whole section is hidden.
    expect(page.get_by_role("heading", name=f"Round {round.number} · {competition.name}")).to_have_count(0)

    page.screenshot(path=".scratch/match_queue_page.png", full_page=True)


def test_empty_match_queue(page: Page, bh: BrowserHelper, db):
    page.goto(bh.reverse("match_queue"))

    expect(page.get_by_text("The queue is empty.")).to_be_visible()
