"""Who is making requests to this site, and what they cost us.

Two halves, deliberately separated:

- `classification` answers "what kind of client is this?" and knows nothing
  about storage. It's the one definition of "is this a real person?", so
  consumers can't drift into slightly different ideas of what a bot is.
- `recording` owns the Redis bucket lifecycle -- writing a classified request,
  and handing unshipped buckets to whatever wants to ship them.

Neither knows about CloudWatch or about Django middleware; those are callers.
See CLAUDE.md here for the reasoning that spans them.
"""

from aiarena.core.traffic.classification import TrafficClass, classify
from aiarena.core.traffic.recording import (
    METRICS,
    REQUEST_COUNT,
    REQUEST_DURATION,
    TRAFFIC_RETENTION_MINUTES,
    Bucket,
    Metric,
    discard,
    drain,
    record,
)


__all__ = [
    "METRICS",
    "REQUEST_COUNT",
    "REQUEST_DURATION",
    "TRAFFIC_RETENTION_MINUTES",
    "Bucket",
    "Metric",
    "TrafficClass",
    "classify",
    "discard",
    "drain",
    "record",
]
