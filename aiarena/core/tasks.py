from django.conf import settings
from django.core import management

import sentry_sdk
from celery import signals
from sentry_sdk.integrations.celery import CeleryIntegration

from aiarena.celery import app
from aiarena.core.utils import sql


@signals.celeryd_init.connect
def init_sentry(**kwargs):
    sentry_sdk.init(
        dsn=settings.SENTRY_DSN,
        integrations=[CeleryIntegration(monitor_beat_tasks=True)],
        release=settings.BUILD_NUMBER,
    )


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
