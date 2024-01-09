from rest_framework.routers import DefaultRouter

from . import views as arenaclient_views


router = DefaultRouter()

# arena client
router.register(r"matches", arenaclient_views.MatchViewSet, basename="match")  # legacy todo: remove once ACs updated
router.register(r"results", arenaclient_views.ResultViewSet, basename="result")  # legacy todo: remove once ACs updated
router.register(r"next-match", arenaclient_views.MatchViewSet, basename="ac_next_match")
router.register(r"submit-result", arenaclient_views.ResultViewSet, basename="ac_submit_result")
router.register(r"set-status", arenaclient_views.SetArenaClientStatusViewSet, basename="api_ac_set_status")


urlpatterns = router.urls
