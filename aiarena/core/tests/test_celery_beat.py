from django.conf import settings

import pytest

from aiarena.celery import app


@pytest.mark.skipif(not hasattr(settings, "CELERY_BEAT_SCHEDULE"), reason="celery beat not configured")
def test_every_beat_entry_points_at_a_registered_task():
    """Beat references tasks by dotted string, so a typo or rename only fails at runtime, silently."""
    app.loader.import_default_modules()
    missing = {
        name: entry["task"] for name, entry in settings.CELERY_BEAT_SCHEDULE.items() if entry["task"] not in app.tasks
    }
    assert missing == {}
