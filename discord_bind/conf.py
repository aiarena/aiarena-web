"""

The MIT License (MIT)

Copyright (c) 2016, Mark Rogaski

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.

"""
from __future__ import unicode_literals

from django.conf import settings
from appconf import AppConf


class DiscordBindConf(AppConf):
    """ Application settings """
    # API service endpoints
    BASE_URI = 'https://discordapp.com/api'
    AUTHZ_PATH = '/oauth2/authorize'
    TOKEN_PATH = '/oauth2/token'

    # OAuth2 application credentials
    CLIENT_ID = None
    CLIENT_SECRET = None

    # OAuth2 scope
    EMAIL_SCOPE = True

    # URI settings
    REDIRECT_URI = None
    INVITE_URI = 'https://discordapp.com/channels/@me'
    RETURN_URI = '/'

    class Meta:
        proxy = True
        prefix = 'discord'
        required = ['CLIENT_ID', 'CLIENT_SECRET']
