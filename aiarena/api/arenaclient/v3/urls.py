from rest_framework.routers import DefaultRouter

from aiarena.api.arenaclient.v3.views import V3MatchViewSet, V3ResultViewSet, V3SetArenaClientStatusViewSet


router = DefaultRouter()

router.register(r"next-match", V3MatchViewSet, basename="v3_ac_next_match")
router.register(r"submit-result", V3ResultViewSet, basename="v3_ac_submit_result")
router.register(r"set-status", V3SetArenaClientStatusViewSet, basename="v3_api_ac_set_status")

urlpatterns = router.urls
