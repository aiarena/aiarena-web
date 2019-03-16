from aiarena.api import views
from rest_framework.routers import DefaultRouter

router = DefaultRouter()
router.register(r'bots', views.BotViewSet, basename='bot')
urlpatterns = router.urls
