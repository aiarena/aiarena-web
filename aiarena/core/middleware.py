from django.http import HttpResponse
from django.shortcuts import render


def maintenance(get_response):
    def middleware(request):
        health_check = request.GET.get("health-check")
        response = HttpResponse(
            render(request, "maintenance.html"),
            status=200 if health_check else 500,
        )
        if health_check:
            response["X-Robots-Tag"] = "noindex"
        return response

    return middleware
