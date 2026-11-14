import pytest
from playwright.sync_api import Page, expect
from rest_framework.authtoken.models import Token

from aiarena.patreon.models import PatreonAccountBind

from ..base import BrowserHelper


pytestmark = [pytest.mark.playwright]


def test_regenerating_api_token_asks_first(page: Page, bh: BrowserHelper, user):
    old_key = Token.objects.create(user=user).key
    bh.log_in(user, page)
    page.goto(bh.reverse("dashboard_profile"))

    # Cancelling leaves the token alone.
    page.get_by_role("button", name="Regenerate").click()
    dialog = page.get_by_role("dialog")
    expect(dialog).to_contain_text("Regenerate your API token?")
    dialog.get_by_role("button", name="Cancel").click()
    expect(dialog).to_have_count(0)
    assert Token.objects.get(user=user).key == old_key

    # Confirming replaces it.
    page.get_by_role("button", name="Regenerate").click()
    page.get_by_role("dialog").get_by_role("button", name="Regenerate").click()
    expect(page.get_by_text("API token regenerated successfully!")).to_be_visible()
    assert Token.objects.get(user=user).key != old_key


def test_generating_first_api_token_does_not_ask(page: Page, bh: BrowserHelper, user):
    bh.log_in(user, page)
    page.goto(bh.reverse("dashboard_profile"))

    page.get_by_role("button", name="Generate").click()

    expect(page.get_by_text("API token generated successfully!")).to_be_visible()
    expect(page.get_by_role("dialog")).to_have_count(0)
    assert Token.objects.filter(user=user).exists()


def test_unlinking_patreon_asks_first(page: Page, bh: BrowserHelper, user):
    PatreonAccountBind.objects.create(user=user, access_token="a", refresh_token="r")
    bh.log_in(user, page)
    page.goto(bh.reverse("dashboard_profile"))
    patreon_row = page.locator("div", has_text="Patreon").filter(has=page.get_by_role("button", name="Unlink")).last

    # Cancelling opens nothing.
    patreon_row.get_by_role("button", name="Unlink").click()
    dialog = page.get_by_role("dialog")
    expect(dialog).to_contain_text("Unlink Patreon?")
    dialog.get_by_role("button", name="Cancel").click()
    expect(dialog).to_have_count(0)
    assert len(page.context.pages) == 1

    # Confirming opens the unlink page.
    patreon_row.get_by_role("button", name="Unlink").click()
    with page.context.expect_page() as unlink_page:
        page.get_by_role("dialog").get_by_role("button", name="Unlink").click()
    unlink_page.value.wait_for_load_state("commit")
    assert unlink_page.value.url.startswith(bh.reverse("unlink_patreon"))
