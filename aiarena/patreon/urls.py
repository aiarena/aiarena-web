from django.urls import re_path

from aiarena.patreon.views import PatreonBindView, PatreonCallbackView


urlpatterns = [
    re_path(r"^$", PatreonBindView.as_view(), name="patreon_bind_index"),
    re_path(r"^oauth/redirect$", PatreonCallbackView.as_view(), name="patreon_oauth_redirect"),
]
