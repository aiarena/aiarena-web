from django.http import HttpResponse
from django.shortcuts import render


def maintenance(get_response):
    def middleware(request):
        return HttpResponse(render(request, "maintenance.html"), status=200)

    return middleware
