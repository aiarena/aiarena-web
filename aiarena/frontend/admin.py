from django import forms
from django.contrib import admin, messages
from django.http import HttpResponseRedirect
from django.utils.safestring import mark_safe

from wiki.editors import getEditor
from wiki.models import ArticleRevision

from aiarena.core.models import (
    ArenaClient,
    ArenaClientStatus,
    Bot,
    BotCrashLimitAlert,
    Competition,
    CompetitionBotMapStats,
    CompetitionBotMatchupStats,
    CompetitionParticipation,
    Map,
    MapPool,
    Match,
    MatchParticipation,
    MatchTag,
    News,
    Result,
    Round,
    ServiceUser,
    Tag,
    Trophy,
    TrophyIcon,
    User,
    WebsiteUser,
)
from aiarena.core.models.bot_race import BotRace
from aiarena.core.models.game import Game
from aiarena.core.models.game_mode import GameMode
from aiarena.core.services import competitions, matches
from aiarena.patreon.models import PatreonAccountBind, PatreonUnlinkedDiscordUID


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
    search_fields = ("username",)
    ordering = ["username"]
    list_display = (
        "username",
        "id",
        "is_active",
        "date_joined",
        "type",
        "owner",
        "trusted",
    )
    list_filter = (
        "date_joined",
        "owner",
        "trusted",
    )
    list_select_related = [
        "owner",
    ]
    raw_id_fields = ["groups", "user_permissions"]
    autocomplete_fields = ["owner"]
    actions = ["activate", "deactivate"]

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
    search_fields = (
        "arenaclient",
        "status",
        "logged_at",
    )
    ordering = (
        "arenaclient",
        "status",
        "logged_at",
    )
    list_display = (
        "arenaclient",
        "status",
        "logged_at",
    )
    list_filter = (
        "arenaclient",
        "status",
    )


@admin.register(Bot)
class BotAdmin(admin.ModelAdmin):
    search_fields = ("name", "user__username")
    list_display = (
        "id",
        "user",
        "name",
        "created",
        "bot_zip",
        "bot_zip_updated",
        "bot_zip_md5hash",
        "bot_zip_publicly_downloadable",
        "bot_data_enabled",
        "bot_data",
        "bot_data_md5hash",
        "bot_data_publicly_downloadable",
        "plays_race",
        "type",
        "game_display_id",
    )
    list_filter = (
        "user",
        "created",
        "bot_zip_updated",
        "bot_zip_publicly_downloadable",
        "bot_data_enabled",
        "bot_data_publicly_downloadable",
        "wiki_article",
    )
    list_select_related = ["user", "plays_race"]
    actions = ["disable_active_participations"]

    def disable_active_participations(self, request, queryset):
        count = 0
        for bot in queryset:
            count += competitions.disable_bot_for_all_competitions(bot)
        self.message_user(
            request, f"Disabled {count} active competition participations for selected bot(s).", messages.SUCCESS
        )

    disable_active_participations.short_description = (
        "Disable all active competition participations for selected bot(s)"
    )


@admin.register(BotCrashLimitAlert)
class BotCrashLimitAlertAdmin(admin.ModelAdmin):
    list_display = (
        "logged_at",
        "triggering_match_participation",
    )
    list_select_related = ["triggering_match_participation"]


@admin.register(BotRace)
class BotRaceAdmin(admin.ModelAdmin):
    search_fields = ("label",)
    list_display = (
        "id",
        "label",
    )
    list_filter = ("label",)


class CompetitionAdminForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        # We can't assume that kwargs['initial'] exists!
        if "initial" not in kwargs:
            kwargs["initial"] = {}

        if "instance" in kwargs and kwargs["instance"] is not None:
            kwargs["initial"].update({"wiki_article_content": kwargs["instance"].wiki_article.current_revision.content})
        super().__init__(*args, **kwargs)

    wiki_article_content = forms.CharField(
        label="Description article content", required=False, widget=getEditor().get_widget()
    )

    def clean_wiki_article_content(self):
        """If the article content changed, save it."""
        if (
            self.instance.wiki_article is not None
            and self.instance.wiki_article.current_revision.content != self.cleaned_data["wiki_article_content"]
        ):
            revision = ArticleRevision()
            revision.inherit_predecessor(self.instance.wiki_article)
            revision.title = self.instance.name
            revision.content = self.cleaned_data["wiki_article_content"]
            revision.deleted = False
            self.instance.wiki_article.add_revision(revision)

    class Meta:
        model = Competition
        exclude = []


@admin.register(Competition)
class CompetitionAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "name",
        "game_mode",
        "date_created",
        "date_opened",
        "date_closed",
        "status",
        "max_active_rounds",
        "interest",
    )
    list_filter = (
        "date_created",
        "date_opened",
        "date_closed",
        "playable_races",
    )
    list_select_related = ["game_mode"]
    # Add the close competition button
    change_form_template = "admin/change_form_competition.html"
    form = CompetitionAdminForm

    def response_change(self, request, obj):
        if "_open-competition" in request.POST:
            error = obj.open()
            if error is None:
                self.message_user(
                    request,
                    "This competition is now open.",
                )
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
        elif "_try-to-close-competition" in request.POST:
            obj.try_to_close()
            if obj.status == "closed":
                self.message_user(request, "This competition is now closed.")
            else:
                self.message_user(
                    request, "This competition cannot be closed. Are there active rounds?", level=messages.ERROR
                )
            return HttpResponseRedirect(".")
        return super().response_change(request, obj)


@admin.register(CompetitionBotMapStats)
class CompetitionBotMapStatsAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "bot",
        "map",
        "match_count",
        "win_count",
        "win_perc",
        "loss_count",
        "loss_perc",
        "tie_count",
        "tie_perc",
        "crash_count",
        "crash_perc",
        "updated",
    )
    # select related bot.competition and bot.bot because they are used to make up the display string
    list_select_related = ["bot", "bot__competition", "bot__bot", "map"]


@admin.register(CompetitionBotMatchupStats)
class CompetitionBotMatchupStatsAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "bot",
        "opponent",
        "match_count",
        "win_count",
        "win_perc",
        "loss_count",
        "loss_perc",
        "tie_count",
        "tie_perc",
        "crash_count",
        "crash_perc",
    )
    list_filter = ("bot", "opponent")
    # select related bot.competition and bot.bot because they are used to make up the display string
    list_select_related = ["bot", "bot__competition", "bot__bot", "opponent", "opponent__competition", "opponent__bot"]


@admin.register(CompetitionParticipation)
class CompetitionParticipationAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "competition",
        "bot",
        "elo",
        "match_count",
        "win_perc",
        "win_count",
        "loss_perc",
        "loss_count",
        "tie_perc",
        "tie_count",
        "crash_perc",
        "crash_count",
        "elo_graph",
        "highest_elo",
        "slug",
    )
    list_filter = ("competition", "bot")
    search_fields = ("slug",)
    list_select_related = ["competition", "bot"]


@admin.register(Game)
class GameAdmin(admin.ModelAdmin):
    list_display = ("name", "map_file_extension")
    search_fields = ("name",)


@admin.register(GameMode)
class GameModeAdmin(admin.ModelAdmin):
    list_display = ("name", "game")
    search_fields = ("name", "game")


@admin.register(Map)
class MapAdmin(admin.ModelAdmin):
    search_fields = ("name",)
    list_display = ("id", "name", "file")
    list_filter = ()


@admin.register(MapPool)
class MapPoolAdmin(admin.ModelAdmin):
    search_fields = ("name",)
    list_display = ("id", "name")
    list_filter = ()


@admin.register(Match)
class MatchAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "map",
        "created",
        "started",
        "assigned_to",
        "round",
        "requested_by",
        "require_trusted_arenaclient",
    )
    list_filter = ("created", "started", "require_trusted_arenaclient")
    search_fields = ["id"]
    actions = ["cancel_matches"]
    list_select_related = ["round", "map", "assigned_to"]
    raw_id_fields = [
        "result",
        "round",
        "assigned_to",
        "requested_by",
        "tags",
    ]

    def cancel_matches(self, request, queryset):
        """
        Registers a MatchCancelled result for the selected matches.
        """
        for match in queryset:
            matches.cancel(match.id)

    cancel_matches.short_description = "Cancel selected matches"


@admin.register(MatchParticipation)
class MatchParticipationAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "match",
        "participant_number",
        "bot",
        "starting_elo",
        "resultant_elo",
        "elo_change",
        "match_log",
        "avg_step_time",
        "result",
        "result_cause",
        "use_bot_data",
        "update_bot_data",
    )
    list_filter = ("use_bot_data", "update_bot_data")
    list_select_related = ["match", "bot"]


@admin.register(MatchTag)
class MatchTagAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "user",
        "tag",
    )
    list_filter = ("user",)
    search_fields = ("tag__name",)
    list_select_related = ["user"]


@admin.register(News)
class NewsAdmin(admin.ModelAdmin):
    list_display = ("created", "title", "text", "yt_link")
    search_fields = ("title",)


@admin.register(PatreonAccountBind)
class PatreonAccountBindAdmin(admin.ModelAdmin):
    list_display = [field.name for field in PatreonAccountBind._meta.fields]
    list_select_related = ["user"]


@admin.register(PatreonUnlinkedDiscordUID)
class PatreonUnlinkedDiscordUIDsAdmin(admin.ModelAdmin):
    list_display = [field.name for field in PatreonUnlinkedDiscordUID._meta.fields]


@admin.register(Result)
class ResultAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "match",
        "winner",
        "type",
        "created",
        "replay_file",
        "game_steps",
        "submitted_by",
        "arenaclient_log",
        "replay_file_has_been_cleaned",
    )
    list_filter = (
        "match",
        "winner",
        "created",
        "submitted_by",
        "replay_file_has_been_cleaned",
    )
    list_select_related = ["match", "winner", "submitted_by"]
    raw_id_fields = [
        "winner",
        "submitted_by",
    ]


@admin.register(Round)
class RoundAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "number",
        "competition",
        "started",
        "finished",
        "complete",
    )
    list_filter = ("competition", "started", "finished", "complete")
    list_select_related = ["competition"]


@admin.register(ServiceUser)
class ServiceUserAdmin(admin.ModelAdmin):
    search_fields = ("username",)
    list_display = (
        "id",
        "password",
        "last_login",
        "is_superuser",
        "username",
        "first_name",
        "last_name",
        "is_staff",
        "is_active",
        "date_joined",
        "email",
        "patreon_level",
        "type",
        "extra_active_competition_participations",
        "extra_periodic_match_requests",
        "receive_email_comms",
    )
    list_filter = (
        "last_login",
        "is_superuser",
        "is_staff",
        "is_active",
        "date_joined",
        "receive_email_comms",
    )
    raw_id_fields = ("groups", "user_permissions")


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "name",
    )
    search_fields = ("name",)


@admin.register(Trophy)
class TrophyAdmin(admin.ModelAdmin):
    list_display = ("id", "bot", "name", "icon")
    list_filter = ("bot",)
    search_fields = ("name",)


@admin.register(TrophyIcon)
class TrophyIconAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "image", "image_preview")
    search_fields = ("name",)
    readonly_fields = ("image_preview",)

    def image_preview(self, obj):
        """
        Used to display the image in the admin panel
        """
        return mark_safe(f'<img src="{obj.image.url}" width="150" height="150" />')

    image_preview.short_description = "Preview"


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    search_fields = ("username",)
    list_display = (
        "id",
        "password",
        "last_login",
        "is_superuser",
        "username",
        "first_name",
        "last_name",
        "is_staff",
        "is_active",
        "date_joined",
        "email",
        "patreon_level",
        "type",
        "extra_active_competition_participations",
        "extra_periodic_match_requests",
        "receive_email_comms",
    )
    list_filter = (
        "last_login",
        "is_superuser",
        "is_staff",
        "is_active",
        "date_joined",
        "receive_email_comms",
    )
    raw_id_fields = ("groups", "user_permissions")


@admin.register(WebsiteUser)
class WebsiteUserAdmin(admin.ModelAdmin):
    search_fields = ("username",)
    list_display = (
        "id",
        "password",
        "last_login",
        "is_superuser",
        "username",
        "first_name",
        "last_name",
        "is_staff",
        "is_active",
        "date_joined",
        "email",
        "patreon_level",
        "type",
        "extra_active_competition_participations",
        "extra_periodic_match_requests",
        "receive_email_comms",
        "single_use_match_requests",
    )
    list_filter = (
        "last_login",
        "is_superuser",
        "is_staff",
        "is_active",
        "date_joined",
        "receive_email_comms",
    )
    raw_id_fields = ("groups", "user_permissions")
    actions = ["ban_users"]

    def ban_users(self, request, queryset):
        from aiarena.core.services.users import Users

        total_banned = 0
        for user in queryset:
            total_banned += Users.ban_user(user)
        self.message_user(
            request,
            f"Banned {queryset.count()} user(s) and disabled {total_banned} bot participations.",
            messages.SUCCESS,
        )

    ban_users.short_description = "Ban selected users (deactivate and disable all their bot participations)"
