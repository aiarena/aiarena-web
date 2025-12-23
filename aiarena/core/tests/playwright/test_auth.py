import pytest
from playwright.sync_api import Page, expect

from ..base import BrowserHelper


pytestmark = [pytest.mark.playwright]


def test_login(page: Page, bh: BrowserHelper, user, admin_user):
    page.goto(bh.reverse("login"))
    page.get_by_label("Username:").fill("billy")
    page.get_by_label("Password:").fill("guest")
    page.get_by_role("button", name="Log in").click()
    page.goto(bh.reverse("dashboard_profile"))
    expect(page.get_by_text("billy")).to_be_visible()


def test_login_with_wrong_credentials(page: Page, bh: BrowserHelper):
    page.goto(bh.reverse("login"))
    page.get_by_label("Username:").fill("test")
    page.get_by_label("Password:").fill("123456")
    page.get_by_role("button", name="Log in").click()
    expect(page.locator("form")).to_contain_text(
        "Please enter a correct username and password. Note that both fields may be case-sensitive."
    )
