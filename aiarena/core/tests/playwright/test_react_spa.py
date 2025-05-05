import pytest
from playwright.sync_api import Page, expect

from ..base import BrowserHelper


pytestmark = [pytest.mark.playwright]


def test_spa_userbots_shows_no_viewer(page: Page, bh: BrowserHelper):
    page.goto(f"{bh.live_server.url}/dashboard/userbots")
    expect(page.locator("text=no viewer")).to_be_visible()


def test_spa_nav_to_django(page: Page, bh: BrowserHelper):
    page.goto(f"{bh.live_server.url}/dashboard/userbots")
    expect(page.locator("text=Home")).to_be_visible()
    page.get_by_role("link", name="Home").click()
    expect(page.locator("text=Welcome to AI Arena!")).to_be_visible(timeout=7_000)


def test_spa_userbots_shows_create_bot(page: Page, bh: BrowserHelper, user, admin_user):
    page.goto(bh.reverse("login"))
    page.get_by_label("Username:").fill("billy")
    page.get_by_label("Password:").fill("guest")
    page.get_by_role("button", name="Log in").click()
    expect(page.locator("#sidebar-items")).to_contain_text("Logged in: billy")

    page.goto(f"{bh.live_server.url}/dashboard/userbots")
    expect(page.get_by_role("button", name="Upload Bot")).to_be_visible(timeout=5_000)
