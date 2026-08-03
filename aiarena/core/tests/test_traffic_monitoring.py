"""The Redis-to-CloudWatch half: counting, timing, and backfilling.

Uses a real (fake) Redis rather than a mock, because what's under test is the
bucket lifecycle itself — a key is unsent iff it exists — and a mock would just
assert that the code calls the functions it calls.
"""

import datetime
from unittest import mock

from django.contrib.auth.models import AnonymousUser
from django.test import RequestFactory

import fakeredis
import pytest

from aiarena.core import tasks as tasks_module
from aiarena.core.middleware import traffic_classification
from aiarena.core.tasks import traffic_monitoring
from aiarena.core.traffic import REQUEST_COUNT, REQUEST_DURATION, TrafficClass
from aiarena.core.traffic import recording as recording_module
from aiarena.core.utils import monitoring_minute_key


@pytest.fixture
def redis():
    """The fake Redis that core.traffic.recording writes to and reads back."""
    server = fakeredis.FakeStrictRedis()
    with mock.patch.object(recording_module, "celery_redis", server):
        yield server


@pytest.fixture
def cloudwatch():
    with mock.patch.object(tasks_module, "cloudwatch") as client:
        yield client


def sent_datapoints(cloudwatch):
    """Every datapoint across all (possibly chunked) put_metric_data calls."""
    datapoints = []
    for call in cloudwatch.put_metric_data.call_args_list:
        assert call.kwargs["Namespace"] == "Traffic"
        datapoints.extend(call.kwargs["MetricData"])
    return datapoints


def find(datapoints, metric_name, traffic_class):
    matches = [
        point
        for point in datapoints
        if point["MetricName"] == metric_name
        and point["Dimensions"] == [{"Name": "TrafficClass", "Value": traffic_class.value}]
    ]
    assert len(matches) == 1, f"expected exactly one {metric_name}/{traffic_class.value}, got {len(matches)}"
    return matches[0]


def run_request(user_agent="curl/8.4.0", duration_s=0.0):
    """Push one request through the middleware, controlling its apparent duration."""

    def get_response(request):
        return mock.sentinel.response

    request = RequestFactory().get("/", HTTP_USER_AGENT=user_agent)
    request.user = AnonymousUser()
    request.auth = None

    # monotonic() is read once before and once after the view.
    with mock.patch("aiarena.core.middleware.time.monotonic", side_effect=[0.0, duration_s]):
        traffic_classification(get_response)(request)


class TestMiddlewareRecording:
    def test_records_both_count_and_duration(self, db, redis):
        run_request(duration_s=1.5)

        assert redis.hgetall(REQUEST_COUNT.key()) == {b"other_bot": b"1"}
        assert redis.hgetall(REQUEST_DURATION.key()) == {b"other_bot": b"1500"}

    def test_counts_accumulate_within_a_minute(self, db, redis):
        run_request(duration_s=0.2)
        run_request(duration_s=0.3)

        assert redis.hget(REQUEST_COUNT.key(), "other_bot") == b"2"
        assert redis.hget(REQUEST_DURATION.key(), "other_bot") == b"500"

    def test_classes_are_tracked_separately(self, db, redis):
        run_request(user_agent="curl/8.4.0", duration_s=0.1)
        run_request(user_agent="Googlebot/2.1", duration_s=0.2)

        assert redis.hgetall(REQUEST_COUNT.key()) == {b"other_bot": b"1", b"search_engine": b"1"}

    def test_buckets_expire(self, db, redis):
        run_request()

        expected = recording_module.TRAFFIC_RETENTION_MINUTES * 60
        assert redis.ttl(REQUEST_COUNT.key()) == expected
        assert redis.ttl(REQUEST_DURATION.key()) == expected

    def test_redis_failure_does_not_break_the_request(self, db):
        """Losing a minute of monitoring is not worth a 500."""
        from redis.exceptions import ConnectionError as RedisConnectionError

        broken = mock.Mock()
        broken.pipeline.side_effect = RedisConnectionError("down")

        with (
            mock.patch.object(recording_module, "celery_redis", broken),
            mock.patch.object(recording_module.sentry_sdk, "capture_exception") as capture,
        ):
            request = RequestFactory().get("/", HTTP_USER_AGENT="curl/8.4.0")
            request.user = AnonymousUser()
            request.auth = None
            response = traffic_classification(lambda r: mock.sentinel.response)(request)

        assert response is mock.sentinel.response
        assert capture.called


class TestEmitter:
    def test_ships_the_previous_minute(self, db, redis, cloudwatch):
        redis.hset(REQUEST_COUNT.key(minutes_from_now=-1), "other_bot", 7)
        redis.hset(REQUEST_DURATION.key(minutes_from_now=-1), "other_bot", 4200)

        traffic_monitoring()

        datapoints = sent_datapoints(cloudwatch)
        assert find(datapoints, "RequestCount", TrafficClass.OTHER_BOT)["Value"] == 7
        assert find(datapoints, "RequestDuration", TrafficClass.OTHER_BOT)["Value"] == 4200

    def test_emits_every_class_including_silent_ones(self, db, redis, cloudwatch):
        """A class that goes quiet must read as 0, not as a gap in the graph."""
        redis.hset(REQUEST_COUNT.key(minutes_from_now=-1), "other_bot", 1)

        traffic_monitoring()

        datapoints = sent_datapoints(cloudwatch)
        assert find(datapoints, "RequestCount", TrafficClass.ARENA_CLIENT)["Value"] == 0
        assert len(datapoints) == len(TrafficClass) * 2

    def test_both_series_ship_even_if_one_has_no_bucket(self, db, redis, cloudwatch):
        """The minute is the unit, so the two series can never fall out of step.

        Sub-millisecond requests round to a 0 duration and leave no duration
        hash. That must still emit a 0 datapoint, not drop the minute from the
        duration graph while the count graph shows traffic.
        """
        redis.hset(REQUEST_COUNT.key(minutes_from_now=-1), "other_bot", 5)

        traffic_monitoring()

        datapoints = sent_datapoints(cloudwatch)
        assert find(datapoints, "RequestCount", TrafficClass.OTHER_BOT)["Value"] == 5
        assert find(datapoints, "RequestDuration", TrafficClass.OTHER_BOT)["Value"] == 0

    def test_units_are_set_per_metric(self, db, redis, cloudwatch):
        redis.hset(REQUEST_COUNT.key(minutes_from_now=-1), "other_bot", 1)

        traffic_monitoring()

        datapoints = sent_datapoints(cloudwatch)
        assert find(datapoints, "RequestCount", TrafficClass.OTHER_BOT)["Unit"] == "Count"
        assert find(datapoints, "RequestDuration", TrafficClass.OTHER_BOT)["Unit"] == "Milliseconds"

    def test_skips_the_current_minute(self, db, redis, cloudwatch):
        """Requests are still landing in it."""
        redis.hset(REQUEST_COUNT.key(), "other_bot", 3)

        traffic_monitoring()

        assert not cloudwatch.put_metric_data.called
        assert redis.exists(REQUEST_COUNT.key())

    def test_drains_shipped_buckets(self, db, redis, cloudwatch):
        """A key that exists is a minute that hasn't been sent — so sent keys must go."""
        redis.hset(REQUEST_COUNT.key(minutes_from_now=-1), "other_bot", 1)
        redis.hset(REQUEST_DURATION.key(minutes_from_now=-1), "other_bot", 10)

        traffic_monitoring()

        assert not redis.exists(REQUEST_COUNT.key(minutes_from_now=-1))
        assert not redis.exists(REQUEST_DURATION.key(minutes_from_now=-1))

    def test_does_nothing_when_there_is_nothing_to_ship(self, db, redis, cloudwatch):
        traffic_monitoring()

        assert not cloudwatch.put_metric_data.called

    def test_rerun_is_a_noop(self, db, redis, cloudwatch):
        """The task runs twice a minute; the second run must not double-count."""
        redis.hset(REQUEST_COUNT.key(minutes_from_now=-1), "other_bot", 1)

        traffic_monitoring()
        cloudwatch.put_metric_data.reset_mock()
        traffic_monitoring()

        assert not cloudwatch.put_metric_data.called


class TestBackfill:
    def test_ships_minutes_missed_while_beat_was_down(self, db, redis, cloudwatch):
        for minutes_ago in (1, 5, 30):
            redis.hset(REQUEST_COUNT.key(minutes_from_now=-minutes_ago), "other_bot", minutes_ago)

        traffic_monitoring()

        counts = {
            point["Timestamp"]: point["Value"]
            for point in sent_datapoints(cloudwatch)
            if point["MetricName"] == "RequestCount"
            and point["Dimensions"] == [{"Name": "TrafficClass", "Value": "other_bot"}]
        }
        assert len(counts) == 3
        for minutes_ago in (1, 5, 30):
            timestamp = datetime.datetime.fromtimestamp(
                monitoring_minute_key(minutes_from_now=-minutes_ago), tz=datetime.UTC
            )
            assert counts[timestamp] == minutes_ago

    def test_each_minute_is_stamped_with_its_own_instant(self, db, redis, cloudwatch):
        """A late emit must land in its real historical bucket, not pile up at "now"."""
        redis.hset(REQUEST_COUNT.key(minutes_from_now=-10), "other_bot", 1)

        traffic_monitoring()

        expected = datetime.datetime.fromtimestamp(monitoring_minute_key(minutes_from_now=-10), tz=datetime.UTC)
        assert {point["Timestamp"] for point in sent_datapoints(cloudwatch)} == {expected}

    def test_replays_oldest_first(self, db, redis, cloudwatch):
        for minutes_ago in (2, 9, 4):
            redis.hset(REQUEST_COUNT.key(minutes_from_now=-minutes_ago), "other_bot", 1)

        traffic_monitoring()

        timestamps = [point["Timestamp"] for point in sent_datapoints(cloudwatch)]
        assert timestamps == sorted(timestamps)

    def test_ignores_buckets_older_than_the_sweep(self, db, redis, cloudwatch):
        beyond = recording_module.TRAFFIC_RETENTION_MINUTES + 1
        redis.hset(REQUEST_COUNT.key(minutes_from_now=-beyond), "other_bot", 1)

        traffic_monitoring()

        assert not cloudwatch.put_metric_data.called

    def test_large_backfill_is_chunked(self, db, redis, cloudwatch):
        """CloudWatch takes at most 1000 datapoints per call."""
        for minutes_ago in range(1, recording_module.TRAFFIC_RETENTION_MINUTES + 1):
            redis.hset(REQUEST_COUNT.key(minutes_from_now=-minutes_ago), "other_bot", 1)

        traffic_monitoring()

        calls = cloudwatch.put_metric_data.call_args_list
        assert len(calls) > 1
        assert all(len(call.kwargs["MetricData"]) <= 1000 for call in calls)
        assert len(sent_datapoints(cloudwatch)) == recording_module.TRAFFIC_RETENTION_MINUTES * len(TrafficClass) * 2

    def test_buckets_survive_a_failed_send(self, db, redis, cloudwatch):
        """If CloudWatch rejects the batch, the next run must be able to retry it."""
        redis.hset(REQUEST_COUNT.key(minutes_from_now=-1), "other_bot", 1)
        cloudwatch.put_metric_data.side_effect = RuntimeError("cloudwatch is down")

        with pytest.raises(RuntimeError):
            traffic_monitoring()

        assert redis.exists(REQUEST_COUNT.key(minutes_from_now=-1))


class TestEndToEnd:
    def test_a_request_lands_on_the_graph(self, db, redis, cloudwatch):
        """Middleware writes, emitter ships — the two halves agree on the key names."""
        run_request(user_agent="Googlebot/2.1", duration_s=2.0)

        # Pretend a minute has passed, so the bucket is eligible.
        redis.rename(REQUEST_COUNT.key(), REQUEST_COUNT.key(minutes_from_now=-1))
        redis.rename(REQUEST_DURATION.key(), REQUEST_DURATION.key(minutes_from_now=-1))

        traffic_monitoring()

        datapoints = sent_datapoints(cloudwatch)
        assert find(datapoints, "RequestCount", TrafficClass.SEARCH_ENGINE)["Value"] == 1
        assert find(datapoints, "RequestDuration", TrafficClass.SEARCH_ENGINE)["Value"] == 2000
