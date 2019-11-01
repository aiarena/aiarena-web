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
import debug_toolbar
from django.conf import settings
from django.conf.urls import include, url
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path
from django.views.generic.base import TemplateView

from aiarena.frontend import views as core_views

urlpatterns = [  # todo: replace usage of url with path for all these
                  path('__debug__/', include(debug_toolbar.urls)),
                  path('admin/', admin.site.urls),
                  url(r'^accounts/', include('registration.backends.default.urls')),
                  url(r'^accounts/', include('django.contrib.auth.urls')),
                  url(r'^$', core_views.Index.as_view(), name='home'),
                  path('api/', include('aiarena.api.urls')),
                  path('ranking/', core_views.Ranking.as_view(), name='ranking'),
                  path('results/', core_views.Results.as_view(), name='results'),
                  path('arenaclients/', core_views.ArenaClients.as_view(), name='arenaclients'),
                  path('arenaclients/<int:pk>/', core_views.ArenaClient.as_view(), name='arenaclient'),
                  path('match-queue/', core_views.MatchQueue.as_view(), name='match_queue'),
                  path('stream/', TemplateView.as_view(template_name='stream.html'), name='stream'),
                  path('bots/', core_views.BotList.as_view(), name='bots'),
                  path('bots/<int:pk>/', core_views.BotDetail.as_view(), name='bot'),
                  path('bots/<int:pk>/edit/', core_views.BotUpdate.as_view(), name='bot_edit'),
                  path('bots/<int:pk>/bot_zip', core_views.BotZipDownloadView.as_view()),
                  path('bots/<int:pk>/bot_data', core_views.BotDataDownloadView.as_view()),
                  path('match-logs/<int:pk>/', core_views.MatchLogDownloadView.as_view()),
                  path('authors/', core_views.AuthorList.as_view(), name='authors'),
                  path('authors/<int:pk>/', core_views.AuthorDetail.as_view(), name='author'),
                  # path('rounds/', core_views.RoundList.as_view(), name='rounds'), # todo
                  path('rounds/<int:pk>/', core_views.RoundDetail.as_view(), name='round'),
                  path('matches/<int:pk>/', core_views.MatchDetail.as_view(), name='match'),
                  path('seasons/', core_views.SeasonList.as_view(), name='seasons'),
                  path('seasons/<int:pk>/', core_views.SeasonDetail.as_view(), name='season'),
                  path('botupload/', core_views.BotUpload.as_view(), name='botupload'),
                  url('avatar/', include('avatar.urls')),
                  path('profile/', core_views.UserProfile.as_view(), name='profile'),
                  path('profile/edit/', core_views.UserProfileUpdate.as_view(), name='profile_edit'),
                  path('notifications/', include('django_nyt.urls')),
                  path('wiki/', include('wiki.urls')),
                  url(r'^discord/', include('discord_bind.urls')),
                  url(r'^patreon/', include('aiarena.patreon.urls')),
              ] + static(settings.MEDIA_URL,
                         document_root=settings.MEDIA_ROOT)  # https://stackoverflow.com/questions/5517950/django-media-url-and-media-root
