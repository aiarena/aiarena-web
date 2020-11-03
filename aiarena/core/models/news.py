from django.core.exceptions import ValidationError
from django.db import models
import urllib.parse as urlparse
from urllib.parse import parse_qs
import re


class News(models.Model):
    date_created = models.DateTimeField(auto_now_add=True)
    title = models.TextField(max_length=20, blank=True, null=True)
    text = models.TextField(max_length=500, blank=False, null=False)
    yt_link = models.URLField(blank=True, null=True)

    def __str__(self):
        if self.title:
            return self.title
        return self.date_created.strftime("%d %b %Y")

    # youtube videos urls need to be in exact format
    def save(self, *args, **kwargs):
        if self.yt_link:
            embedded_youtube_regex = re.compile('^https:\\/\\/www\\.youtube\\.com\\/embed\\/([a-zA-Z0-9])+$')
            valid_url = re.compile('^https:\\/\\/www\\.youtube\\.com\\/(embed\\/|watch\\?v)')
            if not embedded_youtube_regex.match(self.yt_link):
                if not valid_url.match(self.yt_link):
                    raise ValidationError("YouTube link needed, with 'https://www.' prefix")
                temp = "https://www.youtube.com/embed/"
                parsed = urlparse.urlparse(self.yt_link)
                temp += parse_qs(parsed.query)['v'][0]
                self.yt_link = temp
        super().save(*args, **kwargs)

