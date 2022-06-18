from rest_framework.routers import DefaultRouter

from aiarena.api import views as publicapi_views
from aiarena.api.stream import views as stream_views
from .arenaclient import views as arenaclient_views

router = DefaultRouter()

router.register(r'bots', publicapi_views.BotViewSet, basename='api_bot')
router.register(r'bot-races', publicapi_views.BotRaceViewSet, basename='api_bot_race')
router.register(r'competitions', publicapi_views.CompetitionViewSet, basename='api_competition')
router.register(r'competition-bot-matchup-stats', publicapi_views.CompetitionBotMatchupStatsViewSet, basename='api_competitionbotmatchupstats')
router.register(r'competition-bot-map-stats', publicapi_views.CompetitionBotMapStatsViewSet, basename='api_competitionbotmapstats')
router.register(r'competition-participations', publicapi_views.CompetitionParticipationViewSet, basename='api_competitionparticipation')
router.register(r'discord-users', publicapi_views.DiscordUserViewSet, basename='api_discord_user')
router.register(r'games', publicapi_views.GameViewSet, basename='api_game')
router.register(r'game-modes', publicapi_views.GameModeViewSet, basename='api_gamemode')
router.register(r'maps', publicapi_views.MapViewSet, basename='api_map')
router.register(r'map-pools', publicapi_views.MapPoolViewSet, basename='api_mappool')
router.register(r'matches', publicapi_views.MatchViewSet, basename='api_match')
router.register(r'match-participations', publicapi_views.MatchParticipationViewSet, basename='api_matchparticipation')
router.register(r'news', publicapi_views.NewsViewSet, basename='api_news')
router.register(r'results', publicapi_views.ResultViewSet, basename='api_result')
router.register(r'rounds', publicapi_views.RoundViewSet, basename='api_round')
router.register(r'users', publicapi_views.UserViewSet, basename='api_user')

# arena client
router.register(r'arenaclient/matches', arenaclient_views.MatchViewSet, basename='match')  # legacy todo: remove once ACs updated
router.register(r'arenaclient/results', arenaclient_views.ResultViewSet, basename='result')  # legacy todo: remove once ACs updated
router.register(r'arenaclient/next-match', arenaclient_views.MatchViewSet, basename='ac_next_match')
router.register(r'arenaclient/submit-result', arenaclient_views.ResultViewSet, basename='ac_submit_result')
router.register(r'arenaclient/set-status', arenaclient_views.SetArenaClientStatusViewSet, basename='api_ac_set_status')

# stream
router.register(r'stream/next-replay', stream_views.StreamNextReplayViewSet, basename='api_stream_nextreplay')


urlpatterns = router.urls
