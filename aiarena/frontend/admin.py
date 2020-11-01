from django.contrib import admin, messages
from django.http import HttpResponseRedirect

from aiarena.core.models import ArenaClient, Bot, Map, Match, MatchParticipation, Result, Round, Season, \
    SeasonBotMatchupStats, SeasonParticipation, Trophy, User, News
from aiarena.patreon.models import PatreonAccountBind


class StackedItemInline(admin.StackedInline):
    classes = ("grp-collapse grp-open",)


class TabularItemInline(admin.TabularInline):
    classes = ("grp-collapse grp-open",)


class BotInline(StackedItemInline):
    model = Bot


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    inlines = [BotInline]
    search_fields = ('username',)
    list_display = (
        'id',
        'password',
        'last_login',
        'is_superuser',
        'username',
        'first_name',
        'last_name',
        'is_staff',
        'is_active',
        'date_joined',
        'email',
        'patreon_level',
        'type',
        'extra_active_bots_per_race',
        'extra_periodic_match_requests',
        'receive_email_comms',
        'can_request_games_for_another_authors_bot',
    )
    list_filter = (
        'last_login',
        'is_superuser',
        'is_staff',
        'is_active',
        'date_joined',
        'receive_email_comms',
        'can_request_games_for_another_authors_bot',
    )
    raw_id_fields = ('groups', 'user_permissions')


@admin.register(ArenaClient)
class ArenaClientAdmin(admin.ModelAdmin):
    search_fields = ('username',)
    list_display = (
        'id',
        'password',
        'last_login',
        'is_superuser',
        'username',
        'first_name',
        'last_name',
        'is_staff',
        'is_active',
        'date_joined',
        'email',
        'patreon_level',
        'type',
        'owner',
        'extra_active_bots_per_race',
        'extra_periodic_match_requests',
        'receive_email_comms',
        'can_request_games_for_another_authors_bot',
        'trusted',
    )
    list_filter = (
        'last_login',
        'is_superuser',
        'is_staff',
        'is_active',
        'date_joined',
        'owner',
        'receive_email_comms',
        'can_request_games_for_another_authors_bot',
        'trusted',
    )


@admin.register(Map)
class MapAdmin(admin.ModelAdmin):
    actions = ['activate', 'deactivate']
    
    search_fields = ('name',)
    list_display = ('id', 'name', 'file', 'active')
    list_filter = ('active',)

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


@admin.register(Season)
class SeasonAdmin(admin.ModelAdmin):
    
    list_display = (
        'id',
        'number',
        'date_created',
        'date_opened',
        'date_closed',
        'status',
        'previous_season_files_cleaned',
    )
    list_filter = (
        'date_created',
        'date_opened',
        'date_closed',
        'previous_season_files_cleaned',
    )
    # Add the close season button
    change_form_template = "admin/change_form_season.html"

    def response_change(self, request, obj):
        if "_open-season" in request.POST or "_open-season" in request.POST.get('action'):
            error = obj.open()
            if error is None:
                self.message_user(request, "This season is now open.",)
            else:
                self.message_user(request, error, level=messages.ERROR)
            return HttpResponseRedirect(".")
        elif "_pause-season" in request.POST or "_pause-season" in request.POST.get('action'):
            error = obj.pause()
            if error is None:
                self.message_user(request, "This season is now paused.")
            else:
                self.message_user(request, error, level=messages.ERROR)
            return HttpResponseRedirect(".")
        elif "_close-season" in request.POST or "_close-season" in request.POST.get('action'):
            error = obj.start_closing()
            if error is None:
                self.message_user(request, "This season is now closing.")
            else:
                self.message_user(request, error, level=messages.ERROR)
            return HttpResponseRedirect(".")
        return super().response_change(request, obj)


@admin.register(Round)
class RoundAdmin(admin.ModelAdmin):
    
    list_display = (
        'id',
        'number',
        'season',
        'started',
        'finished',
        'complete',
    )
    list_filter = ('season', 'started', 'finished', 'complete')


@admin.register(Match)
class MatchAdmin(admin.ModelAdmin):
    
    list_display = (
        'id',
        'map',
        'created',
        'started',
        'assigned_to',
        'round',
        'requested_by',
        'require_trusted_arenaclient',
    )
    list_filter = ('created', 'started', 'require_trusted_arenaclient')
    search_fields = ['id']
    actions = ['cancel_matches']

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


@admin.register(Bot)
class BotAdmin(admin.ModelAdmin):
    
    search_fields = ('name', 'user')
    list_display = (
        'id',
        'user',
        'name',
        'created',
        'active',
        'bot_zip',
        'bot_zip_updated',
        'bot_zip_md5hash',
        'bot_zip_publicly_downloadable',
        'bot_data_enabled',
        'bot_data',
        'bot_data_md5hash',
        'bot_data_publicly_downloadable',
        'plays_race',
        'type',
        'game_display_id',
        'wiki_article',
    )
    list_filter = (
        'user',
        'created',
        'active',
        'bot_zip_updated',
        'bot_zip_publicly_downloadable',
        'bot_data_enabled',
        'bot_data_publicly_downloadable',
        'wiki_article',
    )


@admin.register(MatchParticipation)
class MatchParticipationAdmin(admin.ModelAdmin):
    
    list_display = (
        'id',
        'match',
        'participant_number',
        'bot',
        'starting_elo',
        'resultant_elo',
        'elo_change',
        'match_log',
        'avg_step_time',
        'result',
        'result_cause',
        'use_bot_data',
        'update_bot_data',
    )
    list_filter = ('use_bot_data', 'update_bot_data')


@admin.register(Result)
class ResultAdmin(admin.ModelAdmin):
    
    list_display = (
        'id',
        'match',
        'winner',
        'type',
        'created',
        'replay_file',
        'game_steps',
        'submitted_by',
        'arenaclient_log',
        'interest_rating',
        'date_interest_rating_calculated',
        'replay_file_has_been_cleaned',
    )
    list_filter = (
        'match',
        'winner',
        'created',
        'submitted_by',
        'date_interest_rating_calculated',
        'replay_file_has_been_cleaned',
    )


@admin.register(SeasonParticipation)
class SeasonParticipationAdmin(admin.ModelAdmin):
    
    list_display = (
        'id',
        'season',
        'bot',
        'elo',
        'match_count',
        'win_perc',
        'win_count',
        'loss_perc',
        'loss_count',
        'tie_perc',
        'tie_count',
        'crash_perc',
        'crash_count',
        'elo_graph',
        'highest_elo',
        'slug',
    )
    list_filter = ('season', 'bot')
    search_fields = ('slug',)


@admin.register(SeasonBotMatchupStats)
class SeasonBotMatchupStatsAdmin(admin.ModelAdmin):
    
    list_display = (
        'id',
        'bot',
        'opponent',
        'match_count',
        'win_count',
        'win_perc',
        'loss_count',
        'loss_perc',
        'tie_count',
        'tie_perc',
        'crash_count',
        'crash_perc',
    )
    list_filter = ('bot', 'opponent')


@admin.register(Trophy)
class TrophyAdmin(admin.ModelAdmin):
    
    list_display = ('id', 'bot', 'name')
    list_filter = ('bot',)
    search_fields = ('name',)


@admin.register(PatreonAccountBind)
class PatreonAccountBindAdmin(admin.ModelAdmin):
    list_display = [field.name for field in PatreonAccountBind._meta.fields]


@admin.register(News)
class NewsAdmin(admin.ModelAdmin):
    list_display = ('date_created', 'title', 'text', 'yt_link')
    search_fields = ('title',)
