from django import forms
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.db import IntegrityError, transaction
from django.db.models import Prefetch
from django.shortcuts import redirect
from django.urls import reverse
from django.utils.safestring import mark_safe
from django.views.generic import CreateView, DeleteView, DetailView, UpdateView

from constance import config
from rest_framework.authtoken.models import Token

from aiarena.core.models import Bot, Match, MatchParticipation, User
from aiarena.core.services import supporters
from aiarena.core.services.service_implementations.internal.matches import CancelResult, cancel
from aiarena.patreon.models import PatreonAccountBind
from discord_bind.models import DiscordUser


class UserProfile(LoginRequiredMixin, DetailView):
    model = User
    redirect_field_name = "next"
    template_name = "profile.html"

    def get_login_url(self):
        return reverse("login")

    def get_success_url(self):
        return reverse("profile")

    def get_object(self, *args, **kwargs):
        return self.request.user

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Add in the user's bots
        context["bot_list"] = self.request.user.bots.all()
        context["max_user_bot_count"] = config.MAX_USER_BOT_COUNT
        context["max_active_active_competition_participations_count"] = (
            self.get_active_competition_participations_limit_display()
        )
        requested_matches = (
            Match.objects.filter(requested_by=self.object)
            .prefetch_related(
                Prefetch("map"),
                Prefetch(
                    "matchparticipation_set",
                    MatchParticipation.objects.select_related("bot"),
                    to_attr="participants",
                ),
            )
            .select_related("result")
        )
        context["requested_matches_in_progress"] = list(
            requested_matches.filter(result__isnull=True).order_by("created")
        )
        context["requested_matches_finished"] = list(
            requested_matches.filter(result__isnull=False).order_by("-started")[:50]
        )
        return context

    def get_active_competition_participations_limit_display(self) -> str | int:
        limit = supporters.get_active_bots_limit(self.request.user)
        return "unlimited" if limit is None else limit

    @transaction.atomic
    def post(self, request, *args, **kwargs):
        match_ids = request.POST.getlist("match_selection")
        # Get and cancel requested matches
        matches = Match.objects.filter(
            pk__in=match_ids, requested_by=self.request.user, result__isnull=True, assigned_to__isnull=True
        )
        if matches:
            message = "Matches " if len(matches) > 1 else "Match "
            for match in matches:
                result = cancel(match.id, request.user)
                if result == CancelResult.MATCH_DOES_NOT_EXIST:  # should basically not happen, but just in case
                    raise Exception(f'Match "{match.id}" does not exist')
                elif result == CancelResult.RESULT_ALREADY_EXISTS:
                    raise Exception(f'A result already exists for match "{match.id}"')
                message += f"<a href='{reverse('match', kwargs={'pk': match.id})}'>{match.id}</a>, "
            message = message[:-2] + " cancelled."
            messages.success(self.request, mark_safe(message))
        else:
            messages.error(self.request, mark_safe("No matches were found for cancellation."))
        return redirect("profile")


class UserTokenDetailView(LoginRequiredMixin, DetailView):
    model = Token
    redirect_field_name = "next"
    template_name = "profile_token.html"
    fields = [
        "user",
    ]

    def get_login_url(self):
        return reverse("login")

    def get_object(self, *args, **kwargs):
        # try auto create the token. If that fails then it must exist, so retrieve it
        try:
            with transaction.atomic():
                token = Token.objects.create(user=self.request.user)
        except IntegrityError:  # already exists
            token = Token.objects.get(user=self.request.user)
        return token

    # Regenerate the API token
    @transaction.atomic
    def post(self, request, *args, **kwargs):
        # delete the token
        token = Token.objects.get(user=self.request.user)
        token.delete()

        # navigating back to the page will auto-create the token
        return redirect("profile_token")


class UnlinkDiscordView(LoginRequiredMixin, DeleteView):
    model = DiscordUser
    template_name = "discord/confirm_unlink.html"

    def get_login_url(self):
        return reverse("login")

    def get_success_url(self):
        return reverse("profile")

    def get_object(self, *args, **kwargs):
        return self.request.user.discord_user


class UnlinkPatreonView(LoginRequiredMixin, DeleteView):
    model = PatreonAccountBind
    template_name = "patreon/confirm_unlink.html"

    def get_login_url(self):
        return reverse("login")

    def get_success_url(self):
        return reverse("profile")

    def get_object(self, *args, **kwargs):
        return self.request.user.patreonaccountbind


class UserProfileUpdateForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ["first_name", "last_name", "receive_email_comms"]


class UserProfileUpdate(SuccessMessageMixin, LoginRequiredMixin, UpdateView):
    form_class = UserProfileUpdateForm
    redirect_field_name = "next"
    template_name = "profile_edit.html"
    success_message = "Profile saved successfully"

    def get_login_url(self):
        return reverse("login")

    def get_success_url(self):
        return reverse("profile")

    def get_object(self, *args, **kwargs):
        return self.request.user


class BotUploadForm(forms.ModelForm):
    class Meta:
        model = Bot
        fields = [
            "name",
            "bot_zip",
            "bot_data_enabled",
            "plays_race",
            "type",
        ]


class BotUpload(SuccessMessageMixin, LoginRequiredMixin, CreateView):
    form_class = BotUploadForm
    redirect_field_name = "next"
    template_name = "botupload.html"
    success_message = (
        "Congratulations on creating your bot. Make sure to sign up to a competition to start playing games."
    )

    def get_login_url(self):
        return reverse("login")

    def get_success_url(self):
        return reverse("profile")

    def get_form_kwargs(self):
        # set the bot's user
        kwargs = super().get_form_kwargs()
        if kwargs["instance"] is None:
            kwargs["instance"] = Bot()
        kwargs["instance"].user = self.request.user
        return kwargs

    def form_valid(self, form):
        if config.BOT_UPLOADS_ENABLED:
            return super().form_valid(form)
        else:
            messages.error(self.request, "Sorry. Requested matches are currently disabled.")
            return self.render_to_response(self.get_context_data(form=form))
