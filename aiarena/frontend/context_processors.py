import hashlib
import os
from datetime import timedelta

from django.conf import settings
from django.core.cache import cache
from django.utils import timezone

from constance import config

from aiarena.core.models import Result, User


def debug(request):
    return {"debug": settings.DEBUG}


def stats(request):
    return {
        "match_count_1h": Result.objects.only("id").filter(created__gte=timezone.now() - timedelta(hours=1)).count,
        "match_count_24h": Result.objects.only("id").filter(created__gte=timezone.now() - timedelta(hours=24)).count,
        "arenaclients": User.objects.only("id").filter(type="ARENA_CLIENT", is_active=True).count,
        "aiarena_settings": settings,
        "random_supporter": User.random_supporter(),
        "config": config,
        "style_md5": style_md5(),
    }


def style_md5() -> str:
    md5_value = cache.get("style_md5")
    if md5_value is None:
        md5_value = md5(os.path.join(settings.BASE_DIR, "aiarena/frontend/static/style.css"))[0:8]
        cache.set("style_md5", md5_value, 3600)
    return md5_value


def md5(fname):
    hash_md5 = hashlib.md5()
    with open(fname, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hash_md5.update(chunk)
    return hash_md5.hexdigest()


def settings_context(request):
    return {
        "MATCH_TAG_REGEX": settings.MATCH_TAG_REGEX,
        "MATCH_TAG_LENGTH_LIMIT": settings.MATCH_TAG_LENGTH_LIMIT,
        "MATCH_TAG_PER_MATCH_LIMIT": settings.MATCH_TAG_PER_MATCH_LIMIT,
    }
