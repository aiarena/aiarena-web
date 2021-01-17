from django.contrib import sitemaps
from django.urls import reverse


class StaticViewSitemap(sitemaps.Sitemap):
    priority = 0.5
    changefreq = 'daily'

    def items(self):
        return ['home', 'ranking', 'results', 'match_queue', 'stream', 'bots', 'authors', 'competitions', 'profile', 'wiki:root',]

    def location(self, item):
        return reverse(item)
