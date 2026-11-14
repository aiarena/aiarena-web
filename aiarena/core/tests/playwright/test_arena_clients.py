from datetime import timedelta

from django.utils import timezone

import pytest
from playwright.sync_api import Page, expect

from aiarena.core.models import Match, MatchParticipation, Result, Round

from ..base import BrowserHelper


pytestmark = [pytest.mark.playwright]


def test_arena_clients_page_lists_clients(page: Page, bh: BrowserHelper, arenaclient_user):
    result = Result.objects.create(type="MatchCancelled", game_steps=0, submitted_by=arenaclient_user)
    Result.objects.filter(id=result.id).update(created=timezone.now() - timedelta(hours=5))

    page.goto(bh.reverse("arenaclients"))

    row = page.get_by_role("row").filter(has_text="ac1")
    # 0 in the last hour, 1 in the last 24 hours.
    expect(row.get_by_role("cell")).to_have_text(["ac1", arenaclient_user.owner.username, "0", "1"])

    row.get_by_role("link", name="ac1").click()
    page.wait_for_url(bh.reverse("arenaclient", args=[arenaclient_user.id]))
    expect(page.get_by_role("heading", name="ac1")).to_be_visible()


def test_arena_client_page(
    page: Page, bh: BrowserHelper, arenaclient_user, queued_match, bot, other_bot, map, competition
):
    queued_match.assigned_to = arenaclient_user
    queued_match.started = timezone.now()
    queued_match.round = Round.objects.create(competition=competition)
    queued_match.save()

    result = Result.objects.create(type="MatchCancelled", game_steps=0, submitted_by=arenaclient_user)
    finished = Match.objects.create(map=map, assigned_to=arenaclient_user, result=result)
    MatchParticipation.objects.create(match=finished, participant_number=1, bot=bot)
    MatchParticipation.objects.create(match=finished, participant_number=2, bot=other_bot)

    page.goto(bh.reverse("arenaclient", args=[arenaclient_user.id]))

    expect(page.get_by_role("heading", name="ac1")).to_be_visible()
    expect(page.get_by_text("Trusted", exact=True)).to_be_visible()
    expect(page.get_by_text("Operated by")).to_contain_text(arenaclient_user.owner.username)
    expect(page.get_by_role("figure")).to_contain_text("Results submitted")

    assigned = page.get_by_role("article").filter(has_text=f"Match ID {queued_match.id}")
    expect(assigned).to_contain_text("In progress")
    expect(assigned).to_contain_text(bot.name)
    expect(assigned).to_contain_text(bot.user.username)
    expect(assigned).to_contain_text(other_bot.name)
    expect(assigned).to_contain_text(map.name)
    expect(assigned).to_contain_text(f"Round {queued_match.round.number}")
    expect(assigned).to_contain_text(competition.name)

    result_row = page.get_by_role("row").filter(has_text=str(finished.id))
    expect(result_row).to_contain_text(bot.name)
    expect(result_row).to_contain_text(other_bot.name)

    page.screenshot(path=".scratch/arena_client_page.png", full_page=True)
