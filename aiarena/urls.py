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
from django.conf.urls import include
from django.conf.urls.static import static
from django.contrib import admin
from django.contrib.sitemaps.views import sitemap
from django.urls import path, re_path
from django.views.generic.base import TemplateView

import debug_toolbar
import private_storage.urls
from drf_yasg import openapi
from drf_yasg.views import get_schema_view
from rest_framework import permissions

from aiarena.frontend import views as core_views
from aiarena.sitemaps import StaticViewSitemap


sitemaps = {
    "static": StaticViewSitemap,
}

schema_view = get_schema_view(
    openapi.Info(
        title="AI Arena API",
        default_version="v1",
        description="AI-Arena API Swagger Documentation",
        terms_of_service="https://aiarena.net/",
        contact=openapi.Contact(email="staff@aiarena.net"),
        license=openapi.License(name="GPLv3"),
    ),
    public=True,
    permission_classes=(permissions.AllowAny,),
)

urlpatterns = [  # todo: replace usage of url with path for all these
    path("__debug__/", include(debug_toolbar.urls)),
    path("health-check/", core_views.health_check, name="health_check"),
    path("health-check-with-db/", core_views.health_check_with_db, name="health_check_with_db"),
    path("500/", core_views.http_500),
    path("grappelli/", include("grappelli.urls")),  # Grappelli URLS
    path("select2/", include("django_select2.urls")),
    path("admin/doc/", include("django.contrib.admindocs.urls")),
    path("admin/", admin.site.urls),
    path("accounts/", include("registration.backends.default.urls")),
    path("accounts/", include("django.contrib.auth.urls")),
    path("", core_views.frontend, name="home"),
    path("api/", include("aiarena.api.urls")),
    path("graphql/", core_views.CustomGraphQLView.as_view(graphiql=True), name="graphql"),
    path("results/", core_views.RecentResults.as_view(), name="results"),
    path("arenaclients/", core_views.ArenaClients.as_view(), name="arenaclients"),
    path("arenaclients/<int:pk>/", core_views.ArenaClientView.as_view(), name="arenaclient"),
    path("match-queue/", core_views.MatchQueue.as_view(), name="match_queue"),
    path("stream/", TemplateView.as_view(template_name="stream.html"), name="stream"),
    path("bots/", core_views.frontend, name="bots"),
    path("bots/downloadable/", core_views.BotDownloadableList.as_view(), name="bots_downloadable"),
    path("bots/<int:pk>/", core_views.BotDetail.as_view(), name="bot"),
    path("bots/<int:pk>/edit/", core_views.BotUpdate.as_view(), name="bot_edit"),
    path("bots/<int:pk>/bot_zip", core_views.BotZipDownloadView.as_view()),
    path("bots/<int:pk>/bot_data", core_views.BotDataDownloadView.as_view()),
    path("bots/<int:pk>/competitions/", core_views.CompetitionParticipationList.as_view(), name="bot_competitions"),
    path(
        "bots/<int:bot_id>/competitions/<int:pk>",
        core_views.CompetitionParticipationUpdate.as_view(),
        name="bot_competition_edit",
    ),
    path("match-logs/<int:pk>/", core_views.MatchLogDownloadView.as_view()),
    path("authors/", core_views.frontend, name="authors"),
    path("authors/<int:pk>/", core_views.frontend, name="author"),
    # path('rounds/', core_views.RoundList.as_view(), name='rounds'), # todo
    path("rounds/<int:pk>/", core_views.frontend, name="round"),
    path("matches/<int:pk>/", core_views.frontend, name="match"),
    path("competitions/", core_views.frontend, name="competitions"),
    path("competitions/<int:pk>/", core_views.frontend, name="competition"),
    path("competitions/stats/<int:pk>/", core_views.BotCompetitionStatsDetail.as_view()),
    path(
        "competitions/stats/<int:pk>/<slug:slug>",
        core_views.BotCompetitionStatsDetail.as_view(),
        name="bot_competition_stats",
    ),
    path("botupload/", core_views.BotUpload.as_view(), name="botupload"),
    path("requestmatch/", core_views.RequestMatch.as_view(), name="requestmatch"),
    path("avatar/", include("avatar.urls")),
    path("swagger/", schema_view.with_ui("swagger", cache_timeout=0), name="schema-swagger-ui"),
    path("finance/", core_views.project_finance, name="finance"),
    path("profile/", core_views.UserProfile.as_view(), name="profile"),
    path("profile/edit/", core_views.UserProfileUpdate.as_view(), name="profile_edit"),
    path("profile/token/", core_views.UserTokenDetailView.as_view(), name="profile_token"),
    path("profile/unlink/discord/", core_views.UnlinkDiscordView.as_view(), name="unlink_discord"),
    path("profile/unlink/patreon/", core_views.UnlinkPatreonView.as_view(), name="unlink_patreon"),
    path("notifications/", include("django_nyt.urls")),
    path("wiki/", include("wiki.urls")),
    path("discord/", include("discord_bind.urls")),
    path("patreon/", include("aiarena.patreon.urls")),
    path("sitemap.xml/", sitemap, {"sitemaps": sitemaps}, name="django.contrib.sitemaps.views.sitemap"),
    path("robots.txt", include("robots.urls")),
    path("private-media/", include(private_storage.urls)),
    path("dashboard/bots/", core_views.frontend, name="dashboard_bots"),
    path("dashboard/match-requests/", core_views.frontend, name="dashboard_match_requests"),
    path("dashboard/profile/", core_views.frontend, name="dashboard_profile"),
    re_path("^dashboard/.*", core_views.frontend, name="dashboard"),
] + static(
    settings.MEDIA_URL, document_root=settings.MEDIA_ROOT
)  # https://stackoverflow.com/questions/5517950/django-media-url-and-media-root

