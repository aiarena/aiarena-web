from rest_framework.routers import DefaultRouter

from .arenaclient import views

router = DefaultRouter()

# arena client
router.register(r'arenaclient/matches', views.MatchViewSet, basename='match')
router.register(r'arenaclient/results', views.ResultViewSet, basename='result')

# todo: public API
# router.register(r'model', views.ModelViewSet, basename='model')

urlpatterns = router.urls
