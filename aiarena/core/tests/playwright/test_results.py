import pytest
from playwright.sync_api import Page, expect

from aiarena.core.models import Match, MatchParticipation, Result

from ..base import BrowserHelper


pytestmark = [pytest.mark.playwright]


def test_results_page_lists_results(page: Page, bh: BrowserHelper, arenaclient_user, bot, other_bot, map):
    result = Result.objects.create(type="MatchCancelled", game_steps=0, submitted_by=arenaclient_user)
    match = Match.objects.create(map=map, result=result)
    MatchParticipation.objects.create(match=match, participant_number=1, bot=bot)
    MatchParticipation.objects.create(match=match, participant_number=2, bot=other_bot)

    page.goto(bh.reverse("results"))

    row = page.get_by_role("row").filter(has_text=bot.name)
    expect(row).to_contain_text(str(match.id))
    expect(row).to_contain_text(other_bot.name)
    expect(row).to_contain_text("Match Cancelled")
