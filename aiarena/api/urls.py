from rest_framework.routers import DefaultRouter

from aiarena.api import views as publicapi_views
from .arenaclient import views as arenaclient_views

router = DefaultRouter()

router.register(r'bots', publicapi_views.BotViewSet, basename='api_bot')
router.register(r'maps', publicapi_views.MapViewSet, basename='api_map')
router.register(r'matches', publicapi_views.MatchViewSet, basename='api_match')
router.register(r'participants', publicapi_views.ParticipantViewSet, basename='api_participant')
router.register(r'results', publicapi_views.ResultViewSet, basename='api_result')
router.register(r'rounds', publicapi_views.RoundViewSet, basename='api_round')
router.register(r'users', publicapi_views.UserViewSet, basename='api_user')

# arena client
router.register(r'arenaclient/matches', arenaclient_views.MatchViewSet, basename='match')  # todo: prefix basename with arenaclient
router.register(r'arenaclient/results', arenaclient_views.ResultViewSet, basename='result')  # todo: prefix basename with arenaclient


urlpatterns = router.urls
