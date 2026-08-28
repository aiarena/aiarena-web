from django.contrib import sitemaps
from django.urls import reverse

from aiarena.core.models import Bot, Competition, User


class StaticViewSitemap(sitemaps.Sitemap):
    priority = 0.5
    changefreq = "daily"

    def items(self):
        return [
            "home",
            "authors",
            "bots",
            "competitions",
            "results",
            "developers",
            "login",
            "wiki:root",
        ]

    def location(self, item):
        return reverse(item)


class BotSitemap(sitemaps.Sitemap):
    priority = 0.5
    changefreq = "daily"

    def items(self):
        return Bot.objects.values_list("id", flat=True)

    def location(self, bot_id):
        return reverse("bot", kwargs={"pk": bot_id})


class AuthorSitemap(sitemaps.Sitemap):
    priority = 0.5
    changefreq = "daily"

    def items(self):
        return User.objects.values_list("id", flat=True)

    def location(self, author_id):
        return reverse("author", kwargs={"pk": author_id})


class CompetitionSitemap(sitemaps.Sitemap):
    priority = 0.5
    changefreq = "daily"

    def items(self):
        return Competition.objects.values_list("id", flat=True)

    def location(self, competition_id):
        return reverse("competition", kwargs={"pk": competition_id})
