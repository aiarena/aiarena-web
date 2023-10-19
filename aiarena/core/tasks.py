from django.conf import settings
from django.core import management

import sentry_sdk
from celery import signals
from sentry_sdk.integrations.celery import CeleryIntegration

from aiarena.celery import app


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
def clean_up_replays():
    management.call_command("cleanupreplays", days=90)


@app.task(ignore_result=True)
def clean_up_match_log_files():
    management.call_command("cleanupmatchlogfiles")


@app.task(ignore_result=True)
def clean_up_arena_client_log_files():
    management.call_command("cleanuparenaclientlogfiles")


@app.task(ignore_result=True)
def generate_stats():
    management.call_command("generatestats")


@app.task(ignore_result=True)
def refresh_patreon_tiers():
    management.call_command("refreshpatreontiers")


@app.task(ignore_result=True)
def timeout_overtime_matches():
    management.call_command("timeoutovertimematches")
