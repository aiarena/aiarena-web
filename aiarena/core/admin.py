from django.contrib import admin

from .models import *


class UserAdmin(admin.ModelAdmin):
    list_display = [field.name for field in User._meta.fields]


class BotAdmin(admin.ModelAdmin):
    list_display = [field.name for field in Bot._meta.fields]


class MapAdmin(admin.ModelAdmin):
    list_display = [field.name for field in Map._meta.fields]


class MatchAdmin(admin.ModelAdmin):
    list_display = [field.name for field in Match._meta.fields]


class ParticipantAdmin(admin.ModelAdmin):
    list_display = [field.name for field in Participant._meta.fields]


class ResultAdmin(admin.ModelAdmin):
    list_display = [field.name for field in Result._meta.fields]


admin.site.register(User, UserAdmin)
admin.site.register(Bot, BotAdmin)
admin.site.register(Map, MapAdmin)
admin.site.register(Match, MatchAdmin)
admin.site.register(Participant, ParticipantAdmin)
admin.site.register(Result, ResultAdmin)
