from django.contrib.auth.models import AnonymousUser
from django.test import RequestFactory
from django.urls import reverse

import pytest
from rest_framework.authtoken.models import Token

from aiarena.core.models import ArenaClient, WebsiteUser
from aiarena.core.traffic import TrafficClass, classify


@pytest.fixture
def arenaclient_user(db, admin_user):
    return ArenaClient.objects.create(
        username="ac1",
        email="ac1@dev.aiarena.net",
        type="ARENA_CLIENT",
        trusted=True,
        owner=admin_user,
    )


@pytest.fixture
def website_user(db):
    return WebsiteUser.objects.create_user(username="human", email="human@dev.aiarena.net", password="pw")


def make_request(path="/", user=None, auth=None, **headers):
    """A request in the state the middleware sees it: after the view has run.

    That means `user` and `auth` are already populated and `resolver_match` is
    set — which is the whole premise of classifying on the way out.
    """
    request = RequestFactory().get(path, **headers)
    request.user = user if user is not None else AnonymousUser()
    request.auth = auth
    return request


class TestAuthenticatedClasses:
    """The classes that only exist because classification runs post-auth."""

    def test_arena_client_is_identified_by_user_not_user_agent(self, arenaclient_user):
        # A browser user agent, so only the resolved user can give the right answer.
        request = make_request(
            user=arenaclient_user,
            auth=Token(key="x", user=arenaclient_user),
            HTTP_USER_AGENT="Mozilla/5.0 (Macintosh) AppleWebKit/537.36 Chrome/120",
        )
        assert classify(request) == TrafficClass.ARENA_CLIENT

    def test_token_authenticated_human_is_programmatic_user(self, website_user):
        request = make_request(user=website_user, auth=Token(key="x", user=website_user))
        assert classify(request) == TrafficClass.PROGRAMMATIC_USER

    def test_session_authenticated_human_is_probably_user(self, website_user):
        """A logged-in person browsing has a user but no token, so isn't programmatic."""
        request = make_request(user=website_user, auth=None, HTTP_USER_AGENT="Mozilla/5.0 Chrome/120")
        assert classify(request) == TrafficClass.PROBABLY_USER

    def test_arena_client_wins_over_programmatic_user(self, arenaclient_user):
        """Both predicates match an arena client; the more specific one must win."""
        request = make_request(user=arenaclient_user, auth=Token(key="x", user=arenaclient_user))
        assert classify(request) == TrafficClass.ARENA_CLIENT


class TestHealthCheck:
    def test_health_check_route_is_classified_by_url_name(self, db):
        request = make_request(path=reverse("health_check"))
        assert classify(request) == TrafficClass.HEALTH_CHECK

    def test_health_check_beats_auth(self, db, arenaclient_user):
        """Checked first so the highest-volume traffic never pays for the auth checks."""
        request = make_request(
            path=reverse("health_check"),
            user=arenaclient_user,
            auth=Token(key="x", user=arenaclient_user),
        )
        assert classify(request) == TrafficClass.HEALTH_CHECK


class TestUserAgentClasses:
    @pytest.mark.parametrize(
        ("user_agent", "expected"),
        [
            ("Mozilla/5.0 (compatible; Googlebot/2.1; +http://www.google.com/bot.html)", TrafficClass.SEARCH_ENGINE),
            ("Mozilla/5.0 AppleWebKit/537.36 (KHTML, like Gecko; compatible; GPTBot/1.2)", TrafficClass.AI_CRAWLER),
            ("Mozilla/5.0 (compatible; AhrefsBot/7.0; +http://ahrefs.com/robot/)", TrafficClass.SEO_CRAWLER),
            ("Mozilla/5.0 (compatible; Discordbot/2.0)", TrafficClass.SOCIAL_UNFURLER),
            ("Mozilla/5.0 zgrab/0.x", TrafficClass.SCANNER),
            ("Mozilla/5.0 (compatible; UptimeRobot/2.0)", TrafficClass.UPTIME_MONITOR),
            ("ELB-HealthChecker/2.0", TrafficClass.HEALTH_CHECK),
            ("python-requests/2.31.0", TrafficClass.OTHER_BOT),
            ("curl/8.4.0", TrafficClass.OTHER_BOT),
            ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/120.0.0.0 Safari/537.36", TrafficClass.PROBABLY_USER),
        ],
    )
    def test_classification(self, db, user_agent, expected):
        assert classify(make_request(user=None, HTTP_USER_AGENT=user_agent)) == expected

    @pytest.mark.parametrize(
        ("user_agent", "expected"),
        [
            # Verbatim from our own ALB logs — these are UAs the rules missed on
            # a first pass over real traffic, kept as regression cases.
            ("Claude-User (claude-code/2.1.220; +https://support.anthropic.com/)", TrafficClass.AI_CRAWLER),
            (
                "Mozilla/5.0 AppleWebKit/537.36 (KHTML, like Gecko); compatible; Perplexity-User/1.0; "
                "+https://perplexity.ai/perplexity-user",
                TrafficClass.AI_CRAWLER,
            ),
            ("Mozilla/5.0 (compatible; cohere-ai/1.0; +https://cohere.com)", TrafficClass.AI_CRAWLER),
            ("Mozilla/5.0 (compatible; YandexFavicons/1.0; +http://yandex.com/bots)", TrafficClass.SEARCH_ENGINE),
            ("Mozilla/5.0 (compatible; YandexImages/3.0; +http://yandex.com/bots)", TrafficClass.SEARCH_ENGINE),
            (
                "Mozilla/5.0 (compatible; coccocbot-web/1.0; +http://help.coccoc.com/searchengine)",
                TrafficClass.SEARCH_ENGINE,
            ),
            (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko; compatible; "
                "Yeti/1.1; +https://naver.me/spd)",
                TrafficClass.SEARCH_ENGINE,
            ),
            (
                "Mozilla/5.0 (X11; Linux x86_64)  AppleWebKit/537.36 (KHTML, like Gecko; Google Web Preview)  "
                "Chrome/150.0.7871.124 Safari/537.36",
                TrafficClass.SEARCH_ENGINE,
            ),
            (
                "Mozilla/5.0 (compatible; SERankingBacklinksBot/1.0; +https://seranking.com/backlinks-crawler)",
                TrafficClass.SEO_CRAWLER,
            ),
            # Default Playwright/Selenium, seen hitting prod for real. Must stay
            # caught — our own browser tests opt out by setting a realistic UA.
            (
                "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) "
                "HeadlessChrome/149.0.7827.55 Safari/537.36",
                TrafficClass.OTHER_BOT,
            ),
        ],
    )
    def test_user_agents_observed_in_production(self, db, user_agent, expected):
        assert classify(make_request(user=None, HTTP_USER_AGENT=user_agent)) == expected

    def test_matching_is_case_insensitive(self, db):
        assert classify(make_request(HTTP_USER_AGENT="GOOGLEBOT/2.1")) == TrafficClass.SEARCH_ENGINE

    def test_specific_class_beats_generic_bot_fallback(self, db):
        """Googlebot contains "bot/", which the OTHER_BOT fallback also matches."""
        assert classify(make_request(HTTP_USER_AGENT="Googlebot/2.1")) == TrafficClass.SEARCH_ENGINE

    @pytest.mark.parametrize("user_agent", ["Ruby", "node", "python", "Java/17.0.2"])
    def test_bare_word_user_agents_match_exactly(self, db, user_agent):
        assert classify(make_request(HTTP_USER_AGENT=user_agent)) == TrafficClass.OTHER_BOT

    @pytest.mark.parametrize(
        "user_agent",
        [
            # "go" is inside "Gecko"/"Google", "java" inside "JavaFX", and the
            # bare-word rules would be catastrophic as substrings.
            "Mozilla/5.0 (Macintosh; Intel Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Safari/605.1.15",
            "JavaFX/8.0",
            "Nodejs-powered-Browser/1.0",
        ],
    )
    def test_bare_word_rules_do_not_match_substrings(self, db, user_agent):
        assert classify(make_request(HTTP_USER_AGENT=user_agent)) == TrafficClass.PROBABLY_USER

    def test_empty_user_agent_on_a_real_route_is_probably_user(self, db):
        """The leftover pile over-counts on purpose rather than guessing "bot"."""
        assert classify(make_request(HTTP_USER_AGENT="")) == TrafficClass.PROBABLY_USER


class TestSuspiciousUser:
    def test_unrouted_path_is_suspicious(self, db):
        request = make_request(path="/wp-config.php", HTTP_USER_AGENT="Mozilla/5.0 Chrome/120")
        assert classify(request) == TrafficClass.SUSPICIOUS_USER

    def test_identified_bot_on_an_unrouted_path_keeps_its_own_class(self, db):
        """The path signal only breaks the tie for traffic nothing else identified."""
        request = make_request(path="/wp-config.php", HTTP_USER_AGENT="Googlebot/2.1")
        assert classify(request) == TrafficClass.SEARCH_ENGINE

    def test_authenticated_user_on_an_unrouted_path_is_not_suspicious(self, db, website_user):
        request = make_request(path="/wp-config.php", user=website_user, auth=Token(key="x", user=website_user))
        assert classify(request) == TrafficClass.PROGRAMMATIC_USER
