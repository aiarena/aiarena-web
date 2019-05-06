from django.conf.urls import include
from django.urls import path
from rest_framework.routers import DefaultRouter

router = DefaultRouter()
# Register here
# router.register(r'model', views.ModelViewSet, basename='model')
urlpatterns = [
                  path('arenaclient/', include('aiarena.api.arenaclient.urls')),
              ] + router.urls
