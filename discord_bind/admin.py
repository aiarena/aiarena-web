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
from django.contrib import admin
from .models import DiscordUser, DiscordInvite


@admin.register(DiscordUser)
class DiscordUserAdmin(admin.ModelAdmin):
    list_display = ('user',
                    'uid',
                    'username',
                    'discriminator',
                    'email')
    list_display_links = ('uid',)
    fieldsets = (
        (None, {
            'fields': ('user',),
        }),
        ('Discord Account', {
            'fields': ('uid',
                       ('username', 'discriminator'),
                       'email', 'avatar'),
        }),
        ('OAuth2', {
            'classes': ('collapse',),
            'fields': ('access_token', 'refresh_token', 'scope', 'expiry'),
        }),
    )
    readonly_fields = ('user',
                       'uid',
                       'access_token',
                       'refresh_token',
                       'scope',
                       'expiry')
    search_fields = ['user__username',
                     'user__email',
                     'username',
                     'discriminator',
                     'uid',
                     'email']


@admin.register(DiscordInvite)
class DiscordInviteAdmin(admin.ModelAdmin):
    list_display = ('code',
                    'active',
                    'description',
                    'guild_name',
                    'channel_name',
                    'channel_type')
    list_display_links = ('code',)
    fieldsets = (
        (None, {
            'fields': (('code', 'active'), 'description', 'groups'),
        }),
        ('Discord Guild', {
            'fields': ('guild_name', 'guild_id', 'guild_icon'),
        }),
        ('Discord Channel', {
            'fields': ('channel_name', 'channel_id', 'channel_type'),
        }),
    )
    readonly_fields = ('guild_name',
                       'guild_id',
                       'guild_icon',
                       'channel_name',
                       'channel_id',
                       'channel_type')
    filter_horizontal = ('groups',)
    actions = ['update_context']

    def update_context(self, request, queryset):
        """ Pull invite details from Discord """
        update = 0
        delete = 0
        invites = queryset.all()
        for invite in invites:
            if invite.update_context():
                update += 1
            else:
                invite.delete()
                delete += 1
        self.message_user(request, '%d updated, %d deleted' % (update, delete))
    update_context.short_description = 'Update invite context'
