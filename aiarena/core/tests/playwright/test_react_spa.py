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
    expect(page.get_by_role("button", name="Upload Bot")).to_be_visible(timeout=10_000)
    # force error
    page.get_by_role("link", name="Home").click()
    expect(page.locator("text=Welcome to AI Arena!")).to_be_visible(timeout=7_000)


# def test_spa_userbots_shows_create_bot(page: Page, bh: BrowserHelper, user, admin_user):
#     page.goto(bh.reverse("login"))
#     page.get_by_label("Username:").fill("billy")
#     page.get_by_label("Password:").fill("guest")
#     page.get_by_role("button", name="Log in").click()
#     expect(page.locator("#sidebar-items")).to_contain_text("Logged in: billy")

#     page.goto(f"{bh.live_server.url}/dashboard/userbots")
#     expect(page.get_by_role("button", name="Upload Bot")).to_be_visible(timeout=5_000)


# def test_spa_userbots_shows_active_competition_participations(page: Page, bh: BrowserHelper, user, admin_user):
#     page.goto(bh.reverse("login"))
#     page.get_by_label("Username:").fill("billy")
#     page.get_by_label("Password:").fill("guest")
#     page.get_by_role("button", name="Log in").click()
#     expect(page.locator("#sidebar-items")).to_contain_text("Logged in: billy")

#     page.goto(f"{bh.live_server.url}/dashboard/userbots")
#     expect(page.get_by_role("button", name="Upload Bot")).to_be_visible(timeout=5_000)
#     page.get_by_role("button", name="Upload Bot").click()

#     # Fill in the form
#     page.get_by_label("Name:").fill("MyBot")
#     # page.get_by_label("Bot ZIP:").set_input_files("tests/assets/test_bot.zip")
#     page.get_by_label("Bot Data Enabled:").check()
#     page.get_by_label("Plays Race:").select_option("Protoss")
#     page.get_by_label("Type:").select_option("python")

#     # Validate values
#     assert page.get_by_label("Name:").input_value() == "MyBot"
#     # assert page.get_by_label("Bot ZIP:").input_value() != ""
#     assert page.get_by_label("Bot Data Enabled:").is_checked()
#     assert page.get_by_label("Plays Race:").input_value() == "Protoss"
#     assert page.get_by_label("Type:").input_value() == "python"
