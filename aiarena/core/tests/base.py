from urllib.parse import urlparse, urlunparse

from django.urls import reverse

from pytest_django.live_server_helper import LiveServer


class BrowserHelper:
    def __init__(self, live_server: LiveServer):
        self.live_server = live_server

    def reverse(self, *args, **kwargs):
        url = reverse(*args, **kwargs)
        parsed = urlparse(url)
        if not parsed.netloc:
            live = urlparse(self.live_server.url)
            parsed = parsed._replace(scheme=live.scheme, netloc=live.netloc)
        return urlunparse(parsed)
