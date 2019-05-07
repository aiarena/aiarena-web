"""aiarena URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.conf import settings
from django.conf.urls import include, url
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path
from django.views.generic.base import TemplateView
import private_storage.urls

from aiarena.core import views as core_views

urlpatterns = [
    path('private-media/bots/<int:pk>/bot_zip', core_views.BotZipDownloadView.as_view()),
    url('^private-media/', include(private_storage.urls)),  # required for django admin
    path('admin/', admin.site.urls),
    url(r'^accounts/', include('registration.backends.default.urls')),
    url(r'^accounts/', include('django.contrib.auth.urls')),
    url(r'^$', TemplateView.as_view(template_name='index.html'), name='home'),
    url('rules', TemplateView.as_view(template_name='rules.html'), name='rules'),
    path('api/', include('aiarena.api.urls')),
    path('ranking/', core_views.Ranking.as_view(), name='ranking'),
    path('results/', core_views.Results.as_view(), name='results'),
    path('bots/', core_views.BotList.as_view(), name='bots'),
    path('bots/<int:pk>/', core_views.BotDetail.as_view(), name='bot'),
    path('authors/', core_views.AuthorList.as_view(), name='authors'),
    path('authors/<int:pk>/', core_views.AuthorDetail.as_view(), name='author'),
    path('botupload/', core_views.BotUpload.as_view(), name='botupload'),
    url('avatar/', include('avatar.urls')),
    path('profile/', core_views.UserProfile.as_view(), name='profile'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)  # https://stackoverflow.com/questions/5517950/django-media-url-and-media-root
