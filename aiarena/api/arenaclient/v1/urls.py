from rest_framework.routers import DefaultRouter

from .views import V1MatchViewSet, V1ResultViewSet, V1SetArenaClientStatusViewSet


router = DefaultRouter()

router.register(r"matches", V1MatchViewSet, basename="v1_match")  # legacy
router.register(r"results", V1ResultViewSet, basename="v1_result")  # legacy
router.register(r"next-match", V1MatchViewSet, basename="v1_ac_next_match")
router.register(r"submit-result", V1ResultViewSet, basename="v1_ac_submit_result")
router.register(r"set-status", V1SetArenaClientStatusViewSet, basename="v1_api_ac_set_status")


urlpatterns = router.urls
