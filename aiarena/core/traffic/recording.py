"""Where a classified request gets written, and how it's read back out.

Both halves of the pipeline live here on purpose. The writer's key names, the
reader's sweep window and the retention TTL are one interlocking set of
decisions -- split them across a middleware module and a tasks module and the
next change to one of them silently invalidates the others. See CLAUDE.md here
for why the bucket lifecycle is shaped this way.

This module owns Redis. It does not know about CloudWatch: the emitter task
asks it for drained buckets and decides what to do with them.
"""

import contextlib
import datetime
from dataclasses import dataclass

from django.conf import settings
from django.http import HttpRequest

import sentry_sdk
from redis import Redis
from redis.exceptions import RedisError

from aiarena.core.traffic.classification import TrafficClass, classify
from aiarena.core.utils import monitoring_minute_key


celery_redis = Redis.from_url(settings.CELERY_BROKER_URL)

TRAFFIC_PREFIX = "traffic"

# How far back the emitter sweeps for minutes it never shipped, and therefore
# how long a bucket has to survive in Redis to still be there when it does. ONE
# NUMBER ON PURPOSE: a TTL shorter than the sweep would expire the very buckets
# the sweep exists to recover, and the failure is invisible -- the graph just
# keeps its gap. An hour is far more than a deploy actually costs; the cost of
# overshooting is a few kilobytes of dead hash.
TRAFFIC_RETENTION_MINUTES = 60


# The two metrics recorded per request, and the CloudWatch names/units they
# ship under. Kept together so a new metric is one entry rather than a matching
# pair of edits in two modules.
#
# BOTH EXIST BECAUSE THEY DISAGREE. Count answers "who is hitting us"; summed
# duration answers "whose requests are actually eating the box". A client making
# a handful of pathological requests a minute is a rounding error on the count
# graph and the tallest band on the duration graph. Dropping either as
# redundant loses that case entirely.
@dataclass(frozen=True)
class Metric:
    key_part: str
    cloudwatch_name: str
    unit: str

    def key(self, minutes_from_now: int = 0) -> str:
        """Redis key for this metric's bucket for a given minute.

        The minute is in the key name, which is what makes a late emit correct
        rather than merely non-crashing: the bucket carries the instant it
        describes, so it can be stamped with that instant instead of "now".
        """
        return f"{TRAFFIC_PREFIX}:{self.key_part}:{monitoring_minute_key(minutes_from_now)}"


REQUEST_COUNT = Metric(key_part="count", cloudwatch_name="RequestCount", unit="Count")
REQUEST_DURATION = Metric(key_part="duration", cloudwatch_name="RequestDuration", unit="Milliseconds")

METRICS = (REQUEST_COUNT, REQUEST_DURATION)


def record(request: HttpRequest, duration_ms: int) -> None:
    """Add one request to the current minute's buckets.

    MUST be called after the view has run -- classification depends on the
    resolved user. See classification.py.

    Never raises on a Redis failure: losing a minute of traffic counts is not
    worth a 500, and Redis being down is already visible everywhere that
    matters.
    """
    try:
        traffic_class = classify(request)

        pipeline = celery_redis.pipeline()
        for metric, amount in ((REQUEST_COUNT, 1), (REQUEST_DURATION, duration_ms)):
            key = metric.key()
            pipeline.hincrby(key, traffic_class.value, amount)
            # See the retention constant for why this and the emitter's sweep
            # window have to be the same number.
            pipeline.expire(key, TRAFFIC_RETENTION_MINUTES * 60)
        pipeline.execute()
    except RedisError as exc:
        sentry_sdk.capture_exception(exc)


@dataclass(frozen=True)
class Bucket:
    """One minute's counts for one metric, ready to ship."""

    metric: Metric
    timestamp: datetime.datetime
    counts: dict[TrafficClass, int]
    redis_key: str


def drain(catchup_minutes: int = TRAFFIC_RETENTION_MINUTES) -> list[Bucket]:
    """Every unshipped bucket, oldest first, with all classes filled in.

    Sweeps a window rather than reading one minute because beat isn't running
    during a deploy -- minutes of dead air, every deploy. That's nearly free
    here: a bucket is deleted once shipped, so any bucket still present is by
    definition unsent, and its key says which minute it belongs to.

    Every class appears in `counts`, including ones with no traffic, so a class
    that goes quiet reads as 0 rather than as a gap. That's the whole point of
    watching this: if a bot changes its user agent and stops being recognised,
    its band drops to zero while probably_user jumps by the same amount, and the
    shape of that swap is the tell.

    The current minute is excluded -- requests are still landing in it.

    Does NOT delete what it returns. The caller confirms the data is safely
    somewhere else first, then calls `discard`; otherwise a transient failure
    downstream would turn into permanently lost data.
    """
    buckets = []

    # Oldest first, so a backfill replays in chronological order.
    for minutes_ago in range(catchup_minutes, 0, -1):
        keys = {metric: metric.key(minutes_from_now=-minutes_ago) for metric in METRICS}
        raw = {metric: celery_redis.hgetall(key) for metric, key in keys.items()}

        # THE MINUTE IS THE UNIT, not the individual metric: if anything was
        # recorded, every metric for that minute ships, even the ones with no
        # hash of their own. Otherwise the series fall out of step -- a minute
        # whose durations all round to zero would vanish from the duration graph
        # while still showing traffic on the count graph, which reads as a
        # monitoring gap rather than as the "fast requests" it actually is.
        #
        # A minute with nothing at all is skipped: either nothing was recorded,
        # or it's already shipped and deleted. Either way it's accounted for --
        # and a genuinely trafficless minute is unreachable in practice, since
        # health checks alone land every few seconds.
        if not any(raw.values()):
            continue

        # The key name is the epoch second of the minute it describes, so this
        # is the instant the sample covers, not the instant we got round to it.
        timestamp = datetime.datetime.fromtimestamp(
            monitoring_minute_key(minutes_from_now=-minutes_ago), tz=datetime.UTC
        )

        for metric, key in keys.items():
            decoded = {name.decode(): int(value) for name, value in raw[metric].items()}
            buckets.append(
                Bucket(
                    metric=metric,
                    timestamp=timestamp,
                    counts={traffic_class: decoded.get(traffic_class.value, 0) for traffic_class in TrafficClass},
                    redis_key=key,
                )
            )

    return buckets


def discard(buckets: list[Bucket]) -> None:
    """Drop buckets that have been shipped, so they're never sent twice."""
    if not buckets:
        return
    with contextlib.suppress(RedisError):
        celery_redis.delete(*(bucket.redis_key for bucket in buckets))
