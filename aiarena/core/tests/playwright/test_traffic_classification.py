from django.contrib.auth.models import AnonymousUser
from django.test import RequestFactory

import pytest
from playwright.sync_api import Page

from aiarena.core.traffic import TrafficClass, classify


pytestmark = [pytest.mark.playwright]


def test_browser_tests_look_like_real_users(page: Page):
    """Our Playwright tests must classify as PROBABLY_USER, not as a bot.

    They exist to emulate a person using the site, so they have to travel the
    same code path a person does. Headless Chromium's default user agent says
    "HeadlessChrome", which we classify as automation on purpose — the browser
    context sets a realistic UA to compensate. If that override is ever dropped,
    the tests silently start exercising the bot path instead, and this fails.
    """
    user_agent = page.evaluate("() => navigator.userAgent")

    assert "HeadlessChrome" not in user_agent

    request = RequestFactory().get("/", HTTP_USER_AGENT=user_agent)
    request.user = AnonymousUser()
    request.auth = None

    assert classify(request) == TrafficClass.PROBABLY_USER
