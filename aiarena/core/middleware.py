import socket
from os import environ

from django.conf import settings
from django.http import HttpRequest, HttpResponse
from django.shortcuts import render
from django.urls import Resolver404, resolve


def maintenance(get_response):
    def middleware(request):
        try:
            match = resolve(request.path)
            health_check = match.url_name == "health_check"
        except Resolver404:
            health_check = False

        response = HttpResponse(
            render(request, "maintenance.html"),
            status=200 if health_check else 500,
        )
        if health_check:
            response["X-Robots-Tag"] = "noindex"
        return response

    return middleware


def view_name(view):
    return f"{view.__module__}.{view.__name__}"


def get_view_name(request):
    try:
        match = resolve(request.path)
    except Resolver404:
        return "non-existent view"

    # If match is a partial, retrieve the original view
    try:
        view = match.func.func
    except AttributeError:
        view = match.func

    return view_name(view)


def track_harakiri_request(get_response):
    def middleware(request: HttpRequest):
        user_id = "AnonymousUser"
        if (user := getattr(request, "user", None)) and user.is_authenticated:
            user_id = str(user.id)

        if settings.SENTRY_DSN and settings.SEND_CRASH_REPORTS:
            environ["SENTRY_DSN"] = settings.SENTRY_DSN

        if settings.SERVER_NAME:
            environ["TRACK_SERVER_NAME"] = settings.SERVER_NAME
        elif hasattr(socket, "gethostname"):  # emulate sentry client behavior
            environ["TRACK_SERVER_NAME"] = socket.gethostname()

        environ["TRACK_BUILD_NUMBER"] = settings.BUILD_NUMBER
        environ["TRACK_USER_ID"] = user_id
        environ["TRACK_VIEW"] = get_view_name(request)
        environ["TRACK_URI"] = request.build_absolute_uri()

        environ["TRACK_REQUEST_FINISHED"] = "0"
        response = get_response(request)
        environ["TRACK_REQUEST_FINISHED"] = "1"
        return response

    return middleware
