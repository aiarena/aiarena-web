"""What kind of client is making this request.

One definition of "who is this?", used by everything that needs to count,
sample or exclude traffic. Before this existed the answer was inlined wherever
it was needed, so each consumer had its own slightly different idea of what a
bot was.

The classes are chosen to be a useful breakdown, not just a bot/not-bot flag --
they're the facet you'd split a traffic graph by, so a category is worth its own
value if you'd want to see it as its own band. That's why search engines, AI
crawlers and uptime monitors are separate despite all being "not a person": a
spike in one means something very different from a spike in another.

CLASSIFICATION HAPPENS AFTER THE VIEW, and that is the load-bearing decision
here. This site's most important traffic is arena clients and scripted API
users, and they are indistinguishable from browsers by user agent -- they're
distinguished by *authentication*. A token can be presented by an arena client
or by a person's own script, and only the resolved user says which. That answer
doesn't exist until the auth stack has run, which for DRF views is inside the
view itself. So the request is classified on the way out, never on the way in.

The knock-on benefit is that the response is available too, so a request can be
counted *and* timed under the same label -- see the note on the two metrics
below for why both exist.

UNKNOWN CLIENTS ARE PROBABLY_USER, ON PURPOSE -- and that class is named for
what it actually is. Every other class is a positive identification; this one is
the leftover pile, so it is always an over-count. A bot we failed to identify
inflates it, which is visible and gets noticed. If the default went the other
way, a new crawler would quietly shrink it instead, and a metric that silently
under-reports is worse than one that visibly over-reports.

WHAT THIS CANNOT DO. Past the authenticated classes, classification is by user
agent, so it only catches clients that identify themselves honestly.
Well-behaved bots do -- crawlers and unfurlers say who they are, because they
want to be recognised. Scanners do the opposite: the highest-volume ones wear a
copied browser user agent. No user-agent rule will ever catch those.

What they can't fake is the URL they asked for, because they're looking for
things we don't have (/.env, /wp-config.php). So there is one non-UA signal
here: unidentified traffic asking for a path with no route lands in
SUSPICIOUS_USER instead of PROBABLY_USER. Read that as a reporting split, not a
verdict -- a person with a stale bookmark produces the same evidence.

That is the limit of what belongs here. This module answers "what kind of client
is this", and *only* reports; it never blocks, drops or rate-limits.
"""

import enum
import re

from django.http import HttpRequest
from django.urls import Resolver404, resolve

from rest_framework.authtoken.models import Token


class TrafficClass(enum.StrEnum):
    # The bots that play the games -- the reason this site exists. Identified by
    # the resolved user being an ArenaClient, which is why classification has to
    # happen after auth.
    ARENA_CLIENT = "arena_client"

    # A human's own script or tool, authenticating with their personal API
    # token. Same shape as an arena client on the wire and deliberately NOT
    # folded in with it: this is the traffic most likely to be someone's runaway
    # loop, and it's only actionable if you can see it apart from the clients
    # doing legitimate match work.
    PROGRAMMATIC_USER = "programmatic_user"

    # Our own infrastructure checking we're alive. Typically the highest-volume
    # class and the least interesting one, which is exactly why it needs its own
    # band -- left unlabelled it drowns everything else.
    HEALTH_CHECK = "health_check"

    # Third-party uptime monitors. Real traffic that costs real capacity, but
    # not a person, and they already have their own alerting.
    UPTIME_MONITOR = "uptime_monitor"

    # Search indexers (Googlebot, Bingbot, ...). Worth their own class because
    # them going quiet is a marketing signal, not an infrastructure one.
    SEARCH_ENGINE = "search_engine"

    # Crawlers harvesting content for AI training or datasets.
    AI_CRAWLER = "ai_crawler"

    # SEO/backlink analysis crawlers.
    SEO_CRAWLER = "seo_crawler"

    # Link unfurlers -- someone pasted a link in Discord/Slack. These are the
    # only "bot" that implies a real person did something.
    SOCIAL_UNFURLER = "social_unfurler"

    # Self-declared vulnerability scanners and internet-wide surveyors that are
    # honest about it. The dishonest majority can't be caught here.
    SCANNER = "scanner"

    # Declares itself a bot but doesn't match anything more specific.
    OTHER_BOT = "other_bot"

    # Unrecognised client that asked for a URL this app has no route for. The
    # one class not based on identity or user agent -- a scanner's user agent is
    # worthless and its *paths* are not.
    SUSPICIOUS_USER = "suspicious_user"

    # Everything we didn't recognise. Mostly real people in browsers, plus every
    # bot that lied about being one -- "probably" is the honest word, and the
    # name says so out loud so nobody reads a graph of this as a verified human
    # count.
    PROBABLY_USER = "probably_user"


# Matched as substrings, case-insensitively, because the interesting token is
# usually buried mid-string: AI crawlers in particular present as
# "Mozilla/5.0 AppleWebKit/537.36 (KHTML, like Gecko; compatible; GPTBot/1.2)".
# Order matters -- the first class with a match wins, so more specific
# categories must come before the generic bot/crawler/spider fallback.
_SUBSTRING_RULES: tuple[tuple[TrafficClass, tuple[str, ...]], ...] = (
    (
        TrafficClass.HEALTH_CHECK,
        ("elb-healthchecker/", "kube-probe/"),
    ),
    (
        TrafficClass.UPTIME_MONITOR,
        (
            "sentryuptimebot",
            "libredtail-http",
            "uptimerobot",
            "pingdom",
            "statuscake",
            "betteruptime",
            "site24x7",
        ),
    ),
    (
        TrafficClass.SEARCH_ENGINE,
        (
            "googlebot",
            "google web preview",
            "bingbot",
            # Yandex splits its crawling across many named bots; match the
            # shared prefix rather than chasing each one.
            "yandexbot",
            "yandexrenderresourcesbot",
            "yandexfavicons",
            "yandeximages",
            "duckduckbot",
            "duckassistbot",
            "baiduspider",
            "applebot",
            "sogou web spider",
            "petalbot",
            "seznambot",
            "coccocbot",
            "yeti/",
            "slurp",
        ),
    ),
    (
        TrafficClass.AI_CRAWLER,
        (
            "gptbot",
            "oai-searchbot",
            # The "-user" agents are fetches triggered by a person asking an
            # assistant about a page, rather than bulk crawling. Same class:
            # still a machine fetching, still never going to sign up.
            "chatgpt-user",
            "claudebot",
            "claude-web",
            "claude-user",
            "anthropic-ai",
            "ccbot",
            "google-extended",
            "perplexitybot",
            "perplexity-user",
            "cohere-ai",
            "bytespider",
            "amazonbot",
            "meta-externalagent",
            "meta-externalfetcher",
            "facebookbot",
            "diffbot",
            "omgili",
            "timpibot",
            "imagesift",
        ),
    ),
    (
        TrafficClass.SEO_CRAWLER,
        (
            "ahrefsbot",
            "semrushbot",
            "mj12bot",
            "dotbot",
            "blexbot",
            "dataforseobot",
            "serankingbacklinksbot",
            "serpstatbot",
            "screaming frog",
            "awariobot",
        ),
    ),
    (
        TrafficClass.SOCIAL_UNFURLER,
        (
            "facebookexternalhit",
            "twitterbot",
            "slackbot",
            "discordbot",
            "telegrambot",
            "whatsapp",
            "linkedinbot",
            "redditbot",
            "embedly",
            "skypeuripreview",
            "pinterest",
        ),
    ),
    (
        TrafficClass.SCANNER,
        (
            "censysinspect",
            "zgrab",
            "masscan",
            "nuclei",
            "internetmeasurement",
            "palo alto networks",
            "genomecrawlerd",
            "netsystemsresearch",
            "expanse,",
            "leakix",
            "stretchoid",
            "criminalip",
            "shodan",
            "odin;",
        ),
    ),
    # Generic fallback: anything still self-declaring as automation. Must stay
    # last so the specific classes above get first refusal.
    (
        TrafficClass.OTHER_BOT,
        (
            # Self-declared automation.
            "bot/",
            "bot;",
            "bot)",
            "bot ",
            "_bot",
            "crawler",
            "spider",
            "scraper",
            "facebot",
            "msnbot",
            # Default user agents of HTTP client libraries. Someone hitting us
            # from a script isn't a person browsing the site, whoever they are.
            #
            # Every token here ends in "/" or is otherwise unambiguous, because
            # the bare language names are landmines: "go" is inside "Gecko" and
            # "Google", "java" is inside "JavaFX", and Ruby's and Node's entire
            # default UA is the single word "Ruby"/"node", which as a substring
            # would match half the internet. Those are matched exactly, below.
            "python-requests/",
            "python-urllib3/",
            "python-urllib/",
            "python-httpx/",
            "aiohttp/",
            "httplib2/",
            "scrapy/",
            "go-http-client/",
            "go-resty/",
            "apache-httpclient/",
            "java-http-client/",
            "okhttp/",
            "ktor-client/",
            "unirest-java/",
            "node-fetch/",
            "axios/",
            "undici",
            "superagent/",
            "deno/",
            "bun/",
            "faraday v",
            "rest-client/",
            "typhoeus",
            "mechanize/",
            "guzzlehttp/",
            "symfony httpclient/",
            "wordpress/",
            "restsharp/",
            "ureq/",
            "isahc/",
            "curl/",
            "wget/",
            "libwww-perl/",
            "mojolicious (perl)",
            "http-tiny/",
            "libsoup/",
            "hackney/",
            "finch/",
            "dart/",
            "httpie/",
            "aria2/",
            "lynx/",
            "powershell/",
            "windowspowershell/",
            "r-curl/",
            "httr2/",
            "http-client/",
            "haskell wreq-",
            "sttp/",
            "akka-http/",
            "pekko-http/",
            "lua-resty-http/",
            "luasocket/",
            "http.jl/",
            "postmanruntime/",
            "insomnia/",
            "apachebench/",
            "siege/",
            "k6/",
            "vegeta/",
            "gatling/",
            # Playwright and Selenium send "HeadlessChrome" by default, and
            # someone pointing default-config automation at us is exactly what
            # this should catch.
            #
            # Our own browser tests are the deliberate exception: they exist to
            # emulate a real user, so they set a realistic user agent and land
            # in probably_user like the traffic they're imitating. See the
            # Playwright fixture in core/tests/.
            "headlesschrome",
        ),
    ),
)


# Clients whose entire default user agent is one generic word. As substrings
# these would be catastrophic ("ruby" is inside "Rubycon", "node" inside
# "Nodejs-powered-Browser"), so they only count on an exact match of the whole
# string. Ruby's Net::HTTP really does send just "Ruby", and Node's global fetch
# just "node".
_EXACT_PROGRAMMATIC_USER_AGENTS = frozenset({"ruby", "node", "python"})

# Java's HttpURLConnection sends "Java/17.0.2" -- needs a digit after the slash
# so it can't match an app that merely has "java" in its name.
_JAVA_USER_AGENT = re.compile(r"^java/\d")

# The health check view, matched by URL name rather than path so moving it in
# urls.py can't silently drop the class. The ALB probe is the highest-volume
# traffic we get and it doesn't send a distinctive user agent, so the route it
# hits is the reliable signal.
_HEALTH_CHECK_URL_NAME = "health_check"


def _resolver_match(request: HttpRequest):
    """Django's resolved route for this request, or None if nothing matched.

    Deliberately asks the router rather than comparing against a list of known
    paths: the set of URLs this app serves is already written down in urls.py,
    so deriving the answer from it means the check can never go stale the way a
    pattern list does. Retiring a route reclassifies its scanner traffic for
    free.

    "Resolves" is a weaker statement than "would return 200" -- a view that 404s
    on a missing object still resolves. That's the right side to err on: it only
    ever under-claims suspicion.

    Django has usually already resolved this and cached it on the request; the
    fallback is for the paths where it hasn't (an early redirect, say).
    """
    if (match := getattr(request, "resolver_match", None)) is not None:
        return match
    try:
        return resolve(request.path_info)
    except Resolver404:
        return None


def classify(request: HttpRequest) -> TrafficClass:
    """Which kind of client sent this request.

    MUST be called after the view has run, so that authentication has resolved.
    Called earlier, every authenticated class silently degrades to a user-agent
    guess -- which for arena clients means landing in PROBABLY_USER and
    swamping it.
    """
    match = _resolver_match(request)

    # Before auth, because the probe is unauthenticated and by far the most
    # frequent thing we serve -- no reason to make it pay for the checks below.
    if match is not None and match.url_name == _HEALTH_CHECK_URL_NAME:
        return TrafficClass.HEALTH_CHECK

    # The whole reason this runs post-view. A token says "not a browser"; the
    # resolved user says which kind of not-a-browser.
    user = getattr(request, "user", None)
    if user is not None and user.is_authenticated:
        if user.is_arenaclient:
            return TrafficClass.ARENA_CLIENT
        if isinstance(getattr(request, "auth", None), Token):
            return TrafficClass.PROGRAMMATIC_USER

    user_agent = request.META.get("HTTP_USER_AGENT", "").strip().lower()

    for traffic_class, needles in _SUBSTRING_RULES:
        if any(needle in user_agent for needle in needles):
            return traffic_class

    if user_agent in _EXACT_PROGRAMMATIC_USER_AGENTS or _JAVA_USER_AGENT.match(user_agent):
        return TrafficClass.OTHER_BOT

    if match is None:
        return TrafficClass.SUSPICIOUS_USER

    return TrafficClass.PROBABLY_USER
