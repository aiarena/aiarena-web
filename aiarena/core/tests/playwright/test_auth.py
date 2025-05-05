import pytest
from playwright.sync_api import Page, expect

from ..base import BrowserHelper


pytestmark = [pytest.mark.playwright]

SPA_ROOT = "http://localhost:8000"


def test_login(page: Page, bh: BrowserHelper, user, admin_user):
    page.goto(bh.reverse("login"))
    page.get_by_label("Username:").fill("billy")
    page.get_by_label("Password:").fill("guest")
    page.get_by_role("button", name="Log in").click()
    expect(page.locator("#sidebar-items")).to_contain_text("Logged in: billy")


def test_login_with_wrong_credentials(page: Page, bh: BrowserHelper):
    page.goto(bh.reverse("login"))
    page.get_by_label("Username:").fill("test")
    page.get_by_label("Password:").fill("123456")
    page.get_by_role("button", name="Log in").click()
    expect(page.locator("form")).to_contain_text(
        "Please enter a correct username and password. Note that both fields may be case-sensitive."
    )


def test_spa_userbots_shows_no_viewer(page: Page, bh: BrowserHelper):
    page.goto(f"{bh.live_server.url}/dashboard/userbots")
    expect(page.locator("text=no viewer")).to_be_visible()


def test_spa_userbots_shows_create_bot(page: Page, bh: BrowserHelper, user, admin_user):
    page.goto(bh.reverse("login"))
    page.get_by_label("Username:").fill("billy")
    page.get_by_label("Password:").fill("guest")
    page.get_by_role("button", name="Log in").click()
    expect(page.locator("#sidebar-items")).to_contain_text("Logged in: billy")

    page.goto(f"{bh.live_server.url}/dashboard/userbots")
    expect(page.get_by_role("button", name="Create! Bot")).to_be_visible(timeout=5_000)
