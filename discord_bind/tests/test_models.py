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
    from unittest.mock import patch, Mock
except ImportError:
    from mock import patch, Mock

from django.test import TestCase
from django.contrib.auth.models import User, Group
from django.db import IntegrityError, transaction

from discord_bind.models import DiscordUser, DiscordInvite


class TestDiscordUser(TestCase):
    """ Test the Discord user model """
    def setUp(self):
        self.user = User.objects.create(username='henry')

    def tearDown(self):
        self.user.delete()

    def test_discord_user(self):
        u = DiscordUser.objects.create(user=self.user,
                                       uid='172150183260323840',
                                       username='Henry G. Tiger',
                                       discriminator='1738')
        self.assertEqual(str(u), '%s.%s' % (u.username, u.discriminator))


class TestDiscordInvite(TestCase):
    """ Test the Discord invite model """
    def setUp(self):
        self.red = Group.objects.create(name='Red Team')
        self.blue = Group.objects.create(name='Blue Team')
        self.invite_json = {"code": "aY1XeQGDKL8iCRvJ",
                            "guild": {
                                "splash": None,
                                "id": "132196927679889408",
                                "icon": "b472e4221e5b24f4de1583be747ca1bd",
                                "name": "Alea Iacta Est"},
                            "channel": {"type": "text",
                                        "id": "132196927679889408",
                                        "name": "general"}}

    def tearDown(self):
        self.red.delete()
        self.blue.delete()
        pass

    def test_discord_invite(self):
        DiscordInvite.objects.create(code='EzqS3tytSpUCa7Lr',
                                     active=True)

        inv = DiscordInvite.objects.create(code='8UQcx0Ychpq1Kmqs',
                                           active=True)
        inv.groups.add(self.blue)

        inv = DiscordInvite.objects.create(code='9dbFpT89bmXzejG9',
                                           active=False)
        inv.groups.add(self.red)

        inv = DiscordInvite.objects.create(code='pMqXoCQT41S7e4LK')
        inv.groups.add(self.red)
        inv.groups.add(self.blue)

        with self.assertRaises(IntegrityError):
            with transaction.atomic():
                DiscordInvite.objects.create(code='EzqS3tytSpUCa7Lr',
                                             active=True)

        self.assertEqual(DiscordInvite.objects.filter(groups=self.blue
                                                      ).count(), 2)
        self.assertEqual(DiscordInvite.objects.filter(groups=self.red
                                                      ).count(), 2)
        self.assertEqual(DiscordInvite.objects.filter(groups__isnull=True
                                                      ).count(), 1)

        self.assertEqual(DiscordInvite.objects.filter(active=True
                                                      ).count(), 2)
        self.assertEqual(DiscordInvite.objects.filter(active=False
                                                      ).count(), 2)

    @patch('discord_bind.models.requests.get')
    def test_invite_update(self, mock_get):
        mock_get.return_value = mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = self.invite_json
        obj = DiscordInvite.objects.create(code='aY1XeQGDKL8iCRvJ')
        obj.update_context()
        mock_get.assert_called_once_with('https://discordapp.com/api'
                                         '/invites/aY1XeQGDKL8iCRvJ')
        self.assertEqual(obj.guild_id, "132196927679889408")
        self.assertEqual(obj.guild_name, "Alea Iacta Est")
        self.assertEqual(obj.guild_icon, "b472e4221e5b24f4de1583be747ca1bd")
        self.assertEqual(obj.channel_id, "132196927679889408")
        self.assertEqual(obj.channel_name, "general")
        self.assertEqual(obj.channel_type, "text")
