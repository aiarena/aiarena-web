from rest_framework.routers import DefaultRouter

from aiarena.api import views as publicapi_views
from .arenaclient import views as arenaclient_views

router = DefaultRouter()

# todo: add more models/endpoints
router.register(r'matches', publicapi_views.MatchViewSet, basename='api_match')
router.register(r'results', publicapi_views.ResultViewSet, basename='api_result')

# arena client
router.register(r'arenaclient/matches', arenaclient_views.MatchViewSet, basename='match')  # todo: prefix basename with arenaclient
router.register(r'arenaclient/results', arenaclient_views.ResultViewSet, basename='result')  # todo: prefix basename with arenaclient


urlpatterns = router.urls
