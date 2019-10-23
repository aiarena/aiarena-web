from django.contrib import admin

from aiarena.core.models import *


# These are ordered the same as in the aiarena/core/models.py file

class MapAdmin(admin.ModelAdmin):
    actions = ['activate', 'deactivate']
    list_display = [field.name for field in Map._meta.fields]

    def activate(self, request, queryset):
        """
        Activates selected maps for play.
        """
        for map in queryset:
            map.activate()

    def deactivate(self, request, queryset):
        """
        Deactivates selected maps for play.
        """
        for map in queryset:
            map.deactivate()

    activate.short_description = "Activate selected maps"
    deactivate.short_description = "Deactivate selected maps"


class UserAdmin(admin.ModelAdmin):
    list_display = [field.name for field in User._meta.fields]


class SeasonAdmin(admin.ModelAdmin):
    list_display = [field.name for field in Season._meta.fields]


class RoundAdmin(admin.ModelAdmin):
    list_display = [field.name for field in Round._meta.fields]


class MatchAdmin(admin.ModelAdmin):
    actions = ['cancel_matches']
    list_display = [field.name for field in Match._meta.fields]

    def cancel_matches(self, request, queryset):
        """
        Registers a MatchCancelled result for the selected matches.

        """
        for match in queryset:
            result = match.cancel(request.user)
            if result == Match.CancelResult.MATCH_DOES_NOT_EXIST:  # should basically not happen, but just in case
                raise Exception('Match "%s" does not exist' % match.id)
            elif result == Match.CancelResult.RESULT_ALREADY_EXISTS:
                raise Exception('A result already exists for match "%s"' % match.id)

    cancel_matches.short_description = "Cancel selected matches"


class BotAdmin(admin.ModelAdmin):
    list_display = [field.name for field in Bot._meta.fields]


class SeasonParticipationAdmin(admin.ModelAdmin):
    list_display = [field.name for field in SeasonParticipation._meta.fields]


class MatchParticipationAdmin(admin.ModelAdmin):
    list_display = [field.name for field in MatchParticipation._meta.fields]


class ResultAdmin(admin.ModelAdmin):
    list_display = [field.name for field in Result._meta.fields]


class StatsBotsAdmin(admin.ModelAdmin):
    list_display = [field.name for field in StatsBots._meta.fields]


class StatsBotMatchupsAdmin(admin.ModelAdmin):
    list_display = [field.name for field in StatsBotMatchups._meta.fields]


admin.site.register(Map, MapAdmin)
admin.site.register(User, UserAdmin)
admin.site.register(Season, SeasonAdmin)
admin.site.register(Round, RoundAdmin)
admin.site.register(Match, MatchAdmin)
admin.site.register(Bot, BotAdmin)
admin.site.register(SeasonParticipation, SeasonParticipationAdmin)
admin.site.register(MatchParticipation, MatchParticipationAdmin)
admin.site.register(Result, ResultAdmin)
admin.site.register(StatsBots, StatsBotsAdmin)
admin.site.register(StatsBotMatchups, StatsBotMatchupsAdmin)
