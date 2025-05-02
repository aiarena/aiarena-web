import json

from django.conf import settings
from django.middleware.csrf import get_token
from django.shortcuts import render

from graphene.utils.str_converters import to_camel_case


def frontend(request, *args, extra_settings: dict | None = None, **kwargs):
    frontend_settings = {
        "csrfToken": get_token(request),
        **(extra_settings or {}),
    }

    copy_from_django_settings = ["ROOT_URL"]
    for name in copy_from_django_settings:
        frontend_name = to_camel_case(name.lower())
        frontend_settings[frontend_name] = getattr(settings, name, "")

    return render(
        request,
        "frontend/frontend.html",
        {
            "frontend_settings": json.dumps(frontend_settings),
            "user": request.user,
        },
    )
