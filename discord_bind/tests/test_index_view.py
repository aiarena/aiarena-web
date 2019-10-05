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

try:
    from unittest.mock import patch, MagicMock
except ImportError:
    from mock import patch, MagicMock
try:
    from urllib.parse import urlparse
except ImportError:
    from urlparse import urlparse
import os

from django.test import TestCase, RequestFactory, override_settings
from django.contrib.sessions.middleware import SessionMiddleware
from django.contrib.auth.models import User, AnonymousUser
from django.core.urlresolvers import reverse

from discord_bind.views import index


class TestAuthorizationRequest(TestCase):
    """ Test the authorization request view """
    def setUp(self):
        self.factory = RequestFactory()
        self.user = User.objects.create_user(username="Hoots",
                                             email="hoots@example.com",
                                             password="test")

    def tearDown(self):
        self.user.delete()

    @override_settings(DISCORD_CLIENT_ID='212763200357720576')
    def test_get_index(self):
        def user_request(user, query=''):
            url = reverse('discord_bind_index')
            if query != '':
                url = url + '?' + query
            request = self.factory.get(url)
            request.user = user
            middleware = SessionMiddleware()
            middleware.process_request(request)
            request.session.save()
            return request

        # Anonymous users should bounce to the login page
        request = user_request(AnonymousUser())
        response = index(request)
        self.assertEqual(response.status_code, 302)
        self.assertTrue('login' in response['location'])

        # Loggied in users bounce to the auth request page
        request = user_request(self.user)
        response = index(request)
        self.assertEqual(response.status_code, 302)
        url = urlparse(response['location'])
        self.assertEqual('https://discordapp.com/api/oauth2/authorize',
                         url.scheme + '://' + url.netloc + url.path)
        self.assertIn('response_type=code', url.query)
        self.assertIn('client_id=212763200357720576', url.query)
        self.assertIn('redirect_uri=http%3A%2F%2Ftestserver%2Fcb', url.query)
        self.assertIn('scope=email+guilds.join', url.query)
        self.assertIn('state=%s' % request.session['discord_bind_oauth_state'],
                      url.query)

        # Limited scope
        with self.settings(DISCORD_EMAIL_SCOPE=False):
            request = user_request(self.user)
            response = index(request)
            url = urlparse(response['location'])
            self.assertIn('scope=identity+guilds.join', url.query)

        # URI settings
        with self.settings(DISCORD_BASE_URI='https://www.example.com/api'):
            request = user_request(self.user)
            response = index(request)
            url = urlparse(response['location'])
            self.assertEqual('https://www.example.com/api/oauth2/authorize',
                             url.scheme + '://' + url.netloc + url.path)

        with self.settings(DISCORD_AUTHZ_PATH='/foo/bar'):
            request = user_request(self.user)
            response = index(request)
            url = urlparse(response['location'])
            self.assertEqual('https://discordapp.com/api/foo/bar',
                             url.scheme + '://' + url.netloc + url.path)

        # redirect uri tests
        request = user_request(self.user, 'redirect_uri=https://foo.bar/cb')
        response = index(request)
        # We don't support this case
        self.assertNotIn('redirect_uri=https%3A%2F%2Ffoo.bar%2Fcb', url.query)

        with self.settings(DISCORD_REDIRECT_URI='https://foo.bar/cb'):
            request = user_request(self.user)
            response = index(request)
            url = urlparse(response['location'])
            self.assertIn('redirect_uri=https%3A%2F%2Ffoo.bar%2Fcb', url.query)

        # invite uri tests
        request = user_request(self.user)
        response = index(request)
        self.assertEqual(request.session['discord_bind_invite_uri'],
                         'https://discordapp.com/channels/@me')

        request = user_request(self.user, 'invite_uri=/foo')
        response = index(request)
        self.assertEqual(request.session['discord_bind_invite_uri'], '/foo')

        with self.settings(DISCORD_INVITE_URI='https://www.example.com/'):
            request = user_request(self.user)
            response = index(request)
            self.assertEqual(request.session['discord_bind_invite_uri'],
                             'https://www.example.com/')

        # return uri tests
        request = user_request(self.user)
        response = index(request)
        self.assertEqual(request.session['discord_bind_return_uri'], '/')

        request = user_request(self.user, 'return_uri=/foo')
        response = index(request)
        self.assertEqual(request.session['discord_bind_return_uri'], '/foo')

        with self.settings(DISCORD_RETURN_URI='https://www.example.com/'):
            request = user_request(self.user)
            response = index(request)
            self.assertEqual(request.session['discord_bind_return_uri'],
                             'https://www.example.com/')
