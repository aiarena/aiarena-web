from aiarena.arenaclientapi import views
from rest_framework.routers import DefaultRouter

router = DefaultRouter()
router.register(r'matches', views.MatchViewSet, basename='match')
router.register(r'results', views.ResultViewSet, basename='result')
urlpatterns = router.urls
