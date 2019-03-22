from aiarena.api import views
from rest_framework.routers import DefaultRouter

router = DefaultRouter()
router.register(r'bots', views.BotViewSet, basename='bot')
router.register(r'maps', views.MapViewSet, basename='map')
router.register(r'matches', views.MatchViewSet, basename='match')
router.register(r'participants', views.ParticipantViewSet, basename='participant')
router.register(r'results', views.ResultViewSet, basename='result')
urlpatterns = router.urls
