from rest_framework.routers import DefaultRouter

from aiarena.api import views as publicapi_views
from aiarena.api.stream import views as stream_views
from .arenaclient import views as arenaclient_views

router = DefaultRouter()

router.register(r'bots', publicapi_views.BotViewSet, basename='api_bot')
router.register(r'maps', publicapi_views.MapViewSet, basename='api_map')
router.register(r'matches', publicapi_views.MatchViewSet, basename='api_match')
router.register(r'match-participations', publicapi_views.MatchParticipationViewSet, basename='api_matchparticipation')
# router.register(r'season-participations', publicapi_views.SeasonParticipationViewSet, basename='api_seasonparticipation')
router.register(r'results', publicapi_views.ResultViewSet, basename='api_result')
router.register(r'rounds', publicapi_views.RoundViewSet, basename='api_round')
router.register(r'seasons', publicapi_views.SeasonViewSet, basename='api_season')
router.register(r'users', publicapi_views.UserViewSet, basename='api_user')

# arena client
router.register(r'arenaclient/matches', arenaclient_views.MatchViewSet, basename='match')  # todo: prefix basename with ac
router.register(r'arenaclient/results', arenaclient_views.ResultViewSet, basename='result')  # todo: prefix basename with ac
router.register(r'arenaclient/set-status', arenaclient_views.SetArenaClientStatusViewSet, basename='api_ac_set_status')

# stream
router.register(r'stream/next-replay', stream_views.StreamNextReplayViewSet, basename='api_stream_nextreplay')


urlpatterns = router.urls
