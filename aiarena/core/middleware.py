from django.http import HttpResponse
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
