from django.urls import path

from aiarena.patreon.views import PatreonBindView, PatreonCallbackView


urlpatterns = [
    path(r"", PatreonBindView.as_view(), name="patreon_bind_index"),
    path(r"oauth/redirect", PatreonCallbackView.as_view(), name="patreon_oauth_redirect"),
]
