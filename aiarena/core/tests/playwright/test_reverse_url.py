"""The frontend `reverseUrl` helper must agree with Django's `reverse`.

`reverseUrl` builds URLs in the SPA from route names generated out of `urls.py`. That
generation is the weak link — a botched conversion silently produces wrong paths that
still type-check. This test closes the loop end to end: for every route the generator
emits, it asserts the browser's `window.reverseUrl(name, params)` returns the same path
that Django's `reverse(name, kwargs)` does. Whatever the two disagree on is a real bug.
"""

from django.urls import NoReverseMatch, reverse

import pytest
from playwright.sync_api import Page

from aiarena.core.management.commands.generate_url_definitions import Command
from aiarena.core.tests.base import BrowserHelper


pytestmark = [pytest.mark.playwright]

# A placeholder value per param. Ints satisfy <int:..> converters; the rest are plain
# segments. `reverse` raises NoReverseMatch if a value doesn't fit the route's converter,
# which lets us skip routes we can't construct a sample for (handled below).
SAMPLE_PARAM_VALUES = {
    "pk": 7,
    "bot_id": 7,
    "id": 7,
    "p_num": 1,
    "content_type_id": 7,
}
DEFAULT_PARAM_VALUE = "sample"


def _sample_kwargs(params: list[str]) -> dict:
    return {param: SAMPLE_PARAM_VALUES.get(param, DEFAULT_PARAM_VALUE) for param in params}


def _reversible_routes() -> list[tuple[str, dict, str]]:
    """(name, kwargs, expected_path) for every generated route Django can reverse."""
    routes = []
    for name, _path, params in Command()._extract_urls():
        kwargs = _sample_kwargs(params)
        try:
            expected = reverse(name, kwargs=kwargs)
        except NoReverseMatch:
            # Catch-all regex routes (e.g. the dashboard `.*`) and anything whose sample
            # values don't satisfy the converter — not cleanly reversible, nothing links to
            # them by name. The named routes that replace them are covered on their own.
            continue
        routes.append((name, kwargs, expected))
    return routes


def test_reverse_url_matches_django_reverse(page: Page, bh: BrowserHelper):
    page.goto(bh.reverse("home"))
    page.wait_for_function("() => typeof window.reverseUrl === 'function'")

    routes = _reversible_routes()
    assert routes, "no reversible routes found — generator or URL config likely broken"

    mismatches = []
    for name, kwargs, expected in routes:
        actual = page.evaluate(
            "([name, params]) => window.reverseUrl(name, params)",
            [name, kwargs or None],
        )
        if actual != expected:
            mismatches.append(f"{name}{kwargs}: django={expected!r} reverseUrl={actual!r}")

    assert not mismatches, "reverseUrl disagrees with Django reverse:\n" + "\n".join(mismatches)
