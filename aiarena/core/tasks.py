import datetime
import json
import os
import time
import tracemalloc
from collections import Counter
from statistics import quantiles

from django.conf import settings
from django.core import management
from django.core.cache import caches

import boto3
import sentry_sdk
from botocore.exceptions import BotoCoreError
from celery import signals
from celery.signals import after_task_publish, celeryd_after_setup, task_postrun, task_prerun
from redis import Redis
from sentry_sdk.integrations.celery import CeleryIntegration

from aiarena.celery import app
from aiarena.core.middleware import raw_time_spent_in_queue_key
from aiarena.core.models import Competition
from aiarena.core.services import competitions
from aiarena.core.utils import ReprJSONEncoder, monitoring_minute_key, sql
from aiarena.loggers import logger


celery_redis = Redis.from_url(settings.CELERY_BROKER_URL)

task_track_cache = caches[settings.CELERY_MONITORING_CACHE_ALIAS]
task_track_timeout = 24 * 60 * 60  # 1 day

worker_queues: list[str] | None = None
worker_id: str | None = None

try:
    cloudwatch = boto3.client("cloudwatch")
except BotoCoreError:
    cloudwatch = None


def task_track_key(task_id):
    return f"{settings.CELERY_MONITORING_TRACK_PREFIX}:{task_id}"


def task_stat_key(task_queue, minutes_from_now=0):
    minute_key = monitoring_minute_key(minutes_from_now)
    return f"{settings.CELERY_MONITORING_STAT_PREFIX}:{task_queue}:{minute_key}"


def task_info_context() -> dict:
    return {
        k: v
        for k, v in {
            "task_container_id": os.environ.get("CONTAINER_ID"),
            "task_worker_id": worker_id,
            "task_worker_queues": worker_queues,
        }.items()
        if v is not None
    }


# noinspection PyUnusedLocal
@celeryd_after_setup.connect
def save_celery_worker_hostname(sender, instance, **kwargs):
    global worker_queues
    global worker_id

    try:
        # Get the `worker` part of the full hostname, e.g `celery@worker1`
        hostname: str = instance.hostname.split("@")[1]
        *worker_queues, worker_id = hostname.split("-")
    except (IndexError, TypeError, ValueError):
        pass


@after_task_publish.connect
def track_task_published(headers, body, *args, **kwargs):
    task_id = headers["id"]
    task_track_cache.set(
        task_track_key(task_id),
        {
            "task_name": headers["task"],
            "task_id": task_id,
            "task_published": time.time(),
            "task_queue": kwargs.get("routing_key"),
        },
        timeout=task_track_timeout,
    )


@task_prerun.connect
def track_task_start(task_id, task, args, kwargs, **other):
    task_start = time.time()
    task_key = task_track_key(task_id)
    props = task_track_cache.get(task_key)
    if not isinstance(props, dict):
        props = {}
    props.update(
        {
            "task_name": task.name,
            "task_start": task_start,
        }
    )
    # Convert task arguments to strings
    props.update(
        json.loads(
            json.dumps(
                {
                    "task_args": args,
                    "task_kwargs": kwargs,
                },
                cls=ReprJSONEncoder,
            )
        )
    )

    task_track_cache.set(task_key, props, timeout=task_track_timeout)

    published_time = props.get("task_published")
    if published_time:
        task_wait = round(task_start - published_time, 3)
        props["task_wait"] = task_wait
        task_queue = props.get("task_queue")
        if task_queue:
            stats_key = task_stat_key(task_queue)
            celery_redis.lpush(stats_key, task_wait)
            # We only need stats for a short period of time, because
            # the monitoring task sends the data for the previous minute only
            celery_redis.expire(stats_key, 5 * 60)

    logger.send(
        {
            "source": "Celery",
            "task_id": task_id,
            "task_pid": os.getpid(),
            **task_info_context(),
            **props,
        },
        log_group="celery-tasks",
    )

    if settings.TRACK_TASKS_MEMORY:
        tracemalloc.start()


@task_postrun.connect
def track_task_end(task_id, task, args, kwargs, retval, state, **other):
    payload = {}

    if settings.TRACK_TASKS_MEMORY:
        # we don't calculate memory diff because we restart malloc trace on every task
        # the stapshot on the task end will contain memory allocated by the task
        snap = tracemalloc.take_snapshot()
        memsize = sum([s.size for s in snap.statistics("filename", True)])

        # stop memory tracing immediately after the task completes to avoid memory overhead
        tracemalloc.stop()
        payload.update(
            {
                "mem_end": memsize,
            }
        )

    cache_key = task_track_key(task_id)
    tracked = task_track_cache.get(cache_key)
    if tracked:
        if isinstance(tracked, dict):
            payload.update(tracked)
            start_time = tracked.get("task_start")
            if start_time:
                payload.update(
                    {
                        "task_duration": round(time.time() - start_time, 3),
                    }
                )

        task_track_cache.delete(cache_key)
    payload.update(
        {
            "source": "Celery",
            "task_id": task_id,
            "task_pid": os.getpid(),
            "task_name": task.name,
            "task_args": args,
            "task_kwargs": kwargs,
            "task_retval": str(retval),
            "task_state": state,
        }
    )
    logger.send(payload, log_group="celery-tasks")


@signals.celeryd_init.connect
def init_sentry(**kwargs):
    sentry_sdk.init(
        dsn=settings.SENTRY_DSN,
        integrations=[CeleryIntegration(monitor_beat_tasks=True)],
        release=settings.BUILD_NUMBER,
    )


@app.task(ignore_result=True)
def celery_queue_monitoring():
    # Queue lengths
    queues = {settings.CELERY_TASK_DEFAULT_QUEUE}
    for config in settings.CELERY_TASK_ROUTES.values():
        if q := config.get("queue"):
            queues.add(q)

    cloudwatch.put_metric_data(
        Namespace="CeleryQueue",
        MetricData=[
            {
                "MetricName": "QueueLength",
                "Dimensions": [{"Name": "Queue", "Value": q}],
                "Value": celery_redis.llen(q),
                "Unit": "Count",
                "Timestamp": datetime.datetime.now(),
            }
            for q in queues
        ],
    )

    # Queue wait stats
    wait_metrics = []
    for key in celery_redis.keys(f"{settings.CELERY_MONITORING_STAT_PREFIX}:*:{monitoring_minute_key(-1)}"):
        key = key.decode()
        task_queue = key.split(":")[1]
        timings = [float(m) for m in celery_redis.lrange(key, 0, -1)]
        if not timings:
            continue

        counter = Counter(timings)
        values, counts = zip(*counter.items())
        wait_metrics.append(
            {
                "MetricName": "TaskWait",
                "Dimensions": [{"Name": "Queue", "Value": task_queue}],
                "Values": values,
                "Counts": counts,
                "Unit": "Seconds",
                "Timestamp": datetime.datetime.now(),
            }
        )

        celery_redis.delete(key)
    if wait_metrics:
        cloudwatch.put_metric_data(Namespace="CeleryQueue", MetricData=wait_metrics)


@app.task(ignore_result=True)
def competitions_monitoring():
    competitions_list = Competition.objects.filter(status__in=["open", "closing"])
    for competition in competitions_list:
        cloudwatch.put_metric_data(
            Namespace="Competitions",
            MetricData=[
                {
                    "MetricName": "QueueLength",
                    "Dimensions": [
                        {"Name": "Competition", "Value": competition.name},
                        {"Name": "Type", "Value": bot_type},
                    ],
                    "Value": total,
                    "Unit": "Count",
                    "Timestamp": datetime.datetime.now(),
                }
                for bot_type, total in competitions.bot_type_stats(competition).items()
            ],
        )


def _calc_percentile(data: list, percentile: int):
    assert 0 < percentile < 100, "Please provide a percentile as a number between 0 and 100"
    assert data
    # Need at least 2 data points for quantiles()
    if len(data) == 1:
        return data[0]
    top_percent = 100 - percentile
    assert 100 % top_percent == 0, f"Cannot calculate exact {percentile} percentile, please select a divisible number"
    n = 100 // top_percent
    return round(quantiles(data, n=n, method="inclusive")[n - 2], 3)


@app.task(ignore_result=True)
def request_queue_monitoring():
    # Record percentiles of raw request time spent in queue
    key = raw_time_spent_in_queue_key(minutes_from_now=-1)
    timings = [float(m) for m in celery_redis.lrange(key, 0, -1)]
    if not timings:
        return

    cloudwatch.put_metric_data(
        Namespace="RequestQueue",
        MetricData=[
            {
                "MetricName": "TimeInQueue",
                "Dimensions": [{"Name": "Percentile", "Value": "P50"}],
                "Value": _calc_percentile(timings, 50),
                "Unit": "Milliseconds",
                "Timestamp": datetime.datetime.now(),
            },
            {
                "MetricName": "TimeInQueue",
                "Dimensions": [{"Name": "Percentile", "Value": "P75"}],
                "Value": _calc_percentile(timings, 75),
                "Unit": "Milliseconds",
                "Timestamp": datetime.datetime.now(),
            },
            {
                "MetricName": "TimeInQueue",
                "Dimensions": [{"Name": "Percentile", "Value": "P95"}],
                "Value": _calc_percentile(timings, 95),
                "Unit": "Milliseconds",
                "Timestamp": datetime.datetime.now(),
            },
            {
                "MetricName": "TimeInQueue",
                "Dimensions": [{"Name": "Percentile", "Value": "P99"}],
                "Value": _calc_percentile(timings, 99),
                "Unit": "Milliseconds",
                "Timestamp": datetime.datetime.now(),
            },
        ],
    )
    celery_redis.delete(key)


@app.task(ignore_result=True)
def celery_exception_test():
    raise Exception("Testing Celery exception")


@app.task(ignore_result=True)
def doglobalfilecleanup():
    management.call_command("doglobalfilecleanup", days=90)


@app.task(ignore_result=True)
def generate_stats():
    management.call_command("generatestats")


@app.task(ignore_result=True)
def generate_stats_graphsonly():
    management.call_command("generatestats", "--graphsonly")


@app.task(ignore_result=True)
def refresh_patreon_tiers():
    management.call_command("refreshpatreontiers")


@app.task(ignore_result=True)
def timeout_overtime_matches():
    management.call_command("timeoutovertimematches")


@app.task(ignore_result=True)
def kill_slow_queries(timeout=settings.SQL_TIME_LIMIT):
    db_name = settings.DATABASES["default"]["NAME"]
    db_user = settings.DATABASES["default"]["USER"]
    slow_queries = sql(
        "select * "
        "from pg_stat_activity "
        "where datname = %s and usename = %s and query_start < (NOW() - interval '%s seconds') "
        "order by backend_start desc",
        (db_name, db_user, timeout),
    )
    query_types = ("select", "update", "delete", "insert")
    for query in slow_queries:
        query_type = query["query"].split(" ")[0].lower()
        if query_type not in query_types:
            continue
        sql("select pg_terminate_backend(%s)", [query["pid"]])
        with sentry_sdk.push_scope() as scope:
            scope.set_context("query", query)
            sentry_sdk.capture_message("Slow query killed")
