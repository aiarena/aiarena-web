from rest_framework.routers import DefaultRouter

from .views import V2MatchViewSet, V2ResultViewSet, V2SetArenaClientStatusViewSet


router = DefaultRouter()

router.register(r"next-match", V2MatchViewSet, basename="v2_ac_next_match")
router.register(r"submit-result", V2ResultViewSet, basename="v2_ac_submit_result")
router.register(r"set-status", V2SetArenaClientStatusViewSet, basename="v2_api_ac_set_status")

urlpatterns = router.urls
