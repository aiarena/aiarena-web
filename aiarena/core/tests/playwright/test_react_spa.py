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
    expect(page.locator("text=Welcome to AI Arena!")).to_be_visible()


def test_spa_userbots_shows_create_bot(page: Page, bh: BrowserHelper, user, admin_user):
    page.goto(bh.reverse("login"))
    page.get_by_label("Username:").fill("billy")
    page.get_by_label("Password:").fill("guest")
    page.get_by_role("button", name="Log in").click()
    expect(page.locator("#sidebar-items")).to_contain_text("Logged in: billy")

    page.goto(f"{bh.live_server.url}/dashboard/userbots")
    expect(page.get_by_role("button", name="Upload Bot")).to_be_visible()


# @pytest.mark.skip(reason="to be implemented once we get tests working")
def test_spa_userbots_shows_active_competition_participations(page: Page, bh: BrowserHelper, user, admin_user):
    page.goto(bh.reverse("login"))
    page.get_by_label("Username:").fill("billy")
    page.get_by_label("Password:").fill("guest")
    page.get_by_role("button", name="Log in").click()
    expect(page.locator("#sidebar-items")).to_contain_text("Logged in: billy")

    page.goto(f"{bh.live_server.url}/dashboard/userbots")
    expect(page.get_by_role("button", name="Upload Bot")).to_be_visible()
    page.get_by_role("button", name="Upload Bot").click()

    # Fill in the form
    page.get_by_label("Name:").fill("MyBot")
    page.get_by_label("Bot ZIP:").set_input_files("./assets/test_bot_python.zip")
    page.get_by_label("Bot Data Enabled:").check()
    page.get_by_label("Plays Race:").select_option("Protoss")
    page.get_by_label("Type:").select_option("python")

    expect(page.get_by_label("Name:")).to_have_value("MyBot")

    expect(page.get_by_label("Bot Data Enabled:")).to_be_checked()

    page.get_by_label("Plays Race:").select_option("Protoss")
    expect(page.get_by_label("Plays Race:")).to_have_value("P")
    page.get_by_label("Plays Race:").select_option("Protoss")
    expect(page.get_by_label("Plays Race:")).to_have_value("P")
    page.get_by_label("Plays Race:").select_option("Protoss")

    page.get_by_label("Type:").select_option("python")
    expect(page.get_by_label("Type:")).to_have_value("python")
    page.locator("form").get_by_role("button", name="Upload Bot").click()

    expect(page.locator("form").get_by_role("button", name="Upload Bot")).not_to_be_visible()
    expect(page.locator("text=MyBot")).to_be_visible()
    # expect snackbar text
