from django.urls import include, path

from rest_framework.routers import DefaultRouter

from .v1 import views as v1_views


urlpatterns = [
    path("v1/", include("aiarena.api.arenaclient.v1.urls")),
    path("v2/", include("aiarena.api.arenaclient.v2.urls")),
]

router = DefaultRouter()

# for backwards compatability, make the default version 1
router.register(r"matches", v1_views.MatchViewSet, basename="match")  # legacy
router.register(r"results", v1_views.ResultViewSet, basename="result")  # legacy
router.register(r"next-match", v1_views.MatchViewSet, basename="ac_next_match")
router.register(r"submit-result", v1_views.ResultViewSet, basename="ac_submit_result")
router.register(r"set-status", v1_views.SetArenaClientStatusViewSet, basename="api_ac_set_status")

urlpatterns += router.urls
