from django.urls import reverse

import pytest
from playwright.sync_api import Page, expect

from ..base import BrowserHelper


pytestmark = [pytest.mark.playwright]


def test_login(page: Page, bh: BrowserHelper, user, admin_user):
    bh.log_in(user, page)
    page.goto(bh.reverse("dashboard_profile"))
    expect(page.get_by_text("billy")).to_be_visible()


def test_login_with_wrong_credentials(page: Page, bh: BrowserHelper):
    page.goto(bh.reverse("login"))
    page.get_by_label("Username").fill("test")
    page.get_by_label("Password").fill("123456")
    page.get_by_role("button", name="Log in").click()
    expect(page.get_by_role("alert")).to_contain_text("Incorrect username or password")


def test_login_follows_next(page: Page, bh: BrowserHelper, user):
    """Login-required pages redirect to `login?next=...`; signing in returns there."""
    page.goto(bh.reverse("login") + "?next=" + reverse("dashboard_profile"))
    page.get_by_label("Username").fill("billy")
    page.get_by_label("Password").fill("guest")
    page.get_by_role("button", name="Log in").click()
    page.wait_for_url(bh.reverse("dashboard_profile"))
    expect(page.get_by_text("billy")).to_be_visible()


def test_register_lands_on_check_your_email(page: Page, bh: BrowserHelper, db):
    """Registering moves straight on to the "check your email" page (the email
    itself is sent in the background) and says the email may take a while."""
    page.goto(bh.reverse("registration_register"))
    page.get_by_label("Username").fill("newbie")
    page.get_by_label("Email").fill("newbie@example.com")
    page.get_by_label("Password", exact=True).fill("a-Strong-pass-123")
    page.get_by_label("Confirm password").fill("a-Strong-pass-123")
    page.get_by_role("button", name="Register").click()

    page.wait_for_url(bh.reverse("registration_complete"))
    status = page.get_by_role("status")
    expect(status).to_contain_text("newbie@example.com")
    expect(status).to_contain_text("can take a few minutes")
