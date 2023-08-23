from django.conf.urls import url

from aiarena.patreon.views import PatreonBindView, PatreonCallbackView


urlpatterns = [
    url(r"^$", PatreonBindView.as_view(), name="patreon_bind_index"),
    url(r"^oauth/redirect$", PatreonCallbackView.as_view(), name="patreon_oauth_redirect"),
]
