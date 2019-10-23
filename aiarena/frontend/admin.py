from django.contrib import admin

from aiarena.core.models import *


class UserAdmin(admin.ModelAdmin):
    list_display = [field.name for field in User._meta.fields]


class BotAdmin(admin.ModelAdmin):
    list_display = [field.name for field in Bot._meta.fields]


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


class ParticipationAdmin(admin.ModelAdmin):
    list_display = [field.name for field in MatchParticipation._meta.fields]


class ResultAdmin(admin.ModelAdmin):
    list_display = [field.name for field in Result._meta.fields]


admin.site.register(User, UserAdmin)
admin.site.register(Bot, BotAdmin)
admin.site.register(Map, MapAdmin)
admin.site.register(Round, RoundAdmin)
admin.site.register(Match, MatchAdmin)
admin.site.register(MatchParticipation, ParticipationAdmin)
admin.site.register(Result, ResultAdmin)
