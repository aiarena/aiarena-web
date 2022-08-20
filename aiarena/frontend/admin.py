from django import forms
from django.contrib import admin, messages
from django.http import HttpResponseRedirect
from wiki.editors import getEditor
from wiki.models import ArticleRevision

from aiarena.core.models import ArenaClient, Bot, Map, Match, MatchParticipation, Result, Round, Competition, \
    CompetitionBotMatchupStats, CompetitionParticipation, Trophy, TrophyIcon, User, News, MapPool, MatchTag, Tag, \
    ArenaClientStatus, WebsiteUser
from aiarena.core.models.bot_race import BotRace
from aiarena.core.models.game import Game
from aiarena.core.models.game_mode import GameMode
from aiarena.patreon.models import PatreonAccountBind, PatreonUnlinkedDiscordUIDs


class StackedItemInline(admin.StackedInline):
    classes = ("grp-collapse grp-open",)


class TabularItemInline(admin.TabularInline):
    classes = ("grp-collapse grp-open",)


class BotInline(StackedItemInline):
    model = Bot


##################################################################
#               PLEASE ORDER THESE ALPHABETICALLY                #
##################################################################


@admin.register(ArenaClient)
class ArenaClientAdmin(admin.ModelAdmin):
    search_fields = ('username',)
    ordering = ['username']
    list_display = (
        'username',
        'id',
        'password',
        'last_login',
        'is_superuser',
        'first_name',
        'last_name',
        'is_staff',
        'is_active',
        'date_joined',
        'email',
        'patreon_level',
        'type',
        'owner',
        'extra_active_competition_participations',
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
    actions = ['activate', 'deactivate']

    def activate(self, request, queryset):
        """
        Activate an AC without having to go into its detail view

        """
        for ac in queryset:
            ac.is_active = True
            ac.save()

    def deactivate(self, request, queryset):
        """
        Deactivate an AC without having to go into its detail view

        """
        for ac in queryset:
            ac.is_active = False
            ac.save()

    activate.short_description = "Activate ArenaClient/s"
    deactivate.short_description = "Deactivate ArenaClient/s"


@admin.register(ArenaClientStatus)
class ArenaClientStatusAdmin(admin.ModelAdmin):
    search_fields = ('arenaclient', 'status', 'logged_at',)
    ordering = ('arenaclient', 'status', 'logged_at',)
    list_display = ('arenaclient', 'status', 'logged_at',)
    list_filter = ('arenaclient', 'status',)


@admin.register(Bot)
class BotAdmin(admin.ModelAdmin):
    search_fields = ('name', 'user__username')
    list_display = (
        'id',
        'user',
        'name',
        'created',
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
        'bot_zip_updated',
        'bot_zip_publicly_downloadable',
        'bot_data_enabled',
        'bot_data_publicly_downloadable',
        'wiki_article',
    )

@admin.register(BotRace)
class BotRaceAdmin(admin.ModelAdmin):
    search_fields = ('label',)
    list_display = (
        'id',
        'label',
    )
    list_filter = (
        'label',
    )


class CompetitionAdminForm(forms.ModelForm):

    def __init__(self, *args, **kwargs):
        # We can't assume that kwargs['initial'] exists!
        if 'initial' not in kwargs:
            kwargs['initial'] = {}

        if 'instance' in kwargs and kwargs['instance'] is not None:
            kwargs['initial'].update({'wiki_article_content': kwargs['instance'].wiki_article.current_revision.content})
        super().__init__(*args, **kwargs)

    wiki_article_content = forms.CharField(label='Description article content', required=False,
                                           widget=getEditor().get_widget())

    def clean_wiki_article_content(self):
        """If the article content changed, save it."""
        if self.instance.wiki_article is not None and self.instance.wiki_article.current_revision.content != self.cleaned_data['wiki_article_content']:
            revision = ArticleRevision()
            revision.inherit_predecessor(self.instance.wiki_article)
            revision.title = self.instance.name
            revision.content = self.cleaned_data['wiki_article_content']
            revision.deleted = False
            self.instance.wiki_article.add_revision(revision)

    class Meta:
        model = Competition
        exclude = []


@admin.register(Competition)
class CompetitionAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'name',
        'type',
        'game_mode',
        'date_created',
        'date_opened',
        'date_closed',
        'status',
        'max_active_rounds',
        'interest',
    )
    list_filter = (
        'date_created',
        'date_opened',
        'date_closed',
        'playable_races',
    )
    # Add the close competition button
    change_form_template = "admin/change_form_competition.html"
    form = CompetitionAdminForm

    def response_change(self, request, obj):
        if "_open-competition" in request.POST:
            error = obj.open()
            if error is None:
                self.message_user(request, "This competition is now open.", )
            else:
                self.message_user(request, error, level=messages.ERROR)
            return HttpResponseRedirect(".")
        elif "_pause-competition" in request.POST:
            error = obj.pause()
            if error is None:
                self.message_user(request, "This competition is now paused.")
            else:
                self.message_user(request, error, level=messages.ERROR)
            return HttpResponseRedirect(".")
        elif "_close-competition" in request.POST:
            error = obj.start_closing()
            if error is None:
                self.message_user(request, "This competition is now closing.")
            else:
                self.message_user(request, error, level=messages.ERROR)
            return HttpResponseRedirect(".")
        return super().response_change(request, obj)


@admin.register(CompetitionBotMatchupStats)
class CompetitionBotMatchupStatsAdmin(admin.ModelAdmin):
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


@admin.register(CompetitionParticipation)
class CompetitionParticipationAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'competition',
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
    list_filter = ('competition', 'bot')
    search_fields = ('slug',)


@admin.register(Game)
class GameAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)


@admin.register(GameMode)
class GameModeAdmin(admin.ModelAdmin):
    list_display = ('name', 'game')
    search_fields = ('name', 'game')


@admin.register(Map)
class MapAdmin(admin.ModelAdmin):
    search_fields = ('name',)
    list_display = ('id', 'name', 'file')
    list_filter = ()


@admin.register(MapPool)
class MapPoolAdmin(admin.ModelAdmin):
    search_fields = ('name',)
    list_display = ('id', 'name')
    list_filter = ()


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


@admin.register(MatchTag)
class MatchTagAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'user',
        'tag',
    )
    list_filter = (
        'user',
    )
    search_fields = ('tag__name',)


@admin.register(News)
class NewsAdmin(admin.ModelAdmin):
    list_display = ('created', 'title', 'text', 'yt_link')
    search_fields = ('title',)


@admin.register(PatreonAccountBind)
class PatreonAccountBindAdmin(admin.ModelAdmin):
    list_display = [field.name for field in PatreonAccountBind._meta.fields]


@admin.register(PatreonUnlinkedDiscordUIDs)
class PatreonUnlinkedDiscordUIDsAdmin(admin.ModelAdmin):
    list_display = [field.name for field in PatreonUnlinkedDiscordUIDs._meta.fields]


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


@admin.register(Round)
class RoundAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'number',
        'competition',
        'started',
        'finished',
        'complete',
    )
    list_filter = ('competition', 'started', 'finished', 'complete')


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'name',
    )
    search_fields = ('name',)


@admin.register(Trophy)
class TrophyAdmin(admin.ModelAdmin):
    list_display = ('id', 'bot', 'name', 'icon')
    list_filter = ('bot',)
    search_fields = ('name',)


@admin.register(TrophyIcon)
class TrophyIconAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'image')
    search_fields = ('name',)


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
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
        'extra_active_competition_participations',
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


@admin.register(WebsiteUser)
class WebsiteUserAdmin(admin.ModelAdmin):
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
        'extra_active_competition_participations',
        'extra_periodic_match_requests',
        'receive_email_comms',
        'can_request_games_for_another_authors_bot',
        'single_use_match_requests'
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
