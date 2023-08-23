import hashlib
import os
from datetime import timedelta

from django.core.cache import cache
from django.utils import timezone

from constance import config

from aiarena import settings
from aiarena.core.models import Bot, Result, User

# these are available globally in the django templates
from aiarena.settings import BASE_DIR


def stats(request):
    return {
        "match_count_1h": Result.objects.only("id").filter(created__gte=timezone.now() - timedelta(hours=1)).count(),
        "match_count_24h": Result.objects.only("id").filter(created__gte=timezone.now() - timedelta(hours=24)).count(),
        "arenaclients": User.objects.only("id").filter(type="ARENA_CLIENT", is_active=True).count(),
        "aiarena_settings": settings,
        "random_supporter": User.random_supporter(),
        "config": config,
        "style_md5": style_md5(),
    }


def style_md5() -> str:
    md5_value = cache.get("style_md5")
    if md5_value is None:
        md5_value = md5(os.path.join(BASE_DIR, "aiarena/frontend/static/style.css"))[0:8]
        cache.set("style_md5", md5_value, 3600)
    return md5_value


def md5(fname):
    hash_md5 = hashlib.md5()
    with open(fname, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hash_md5.update(chunk)
    return hash_md5.hexdigest()
