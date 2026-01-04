from django import forms
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import ValidationError
from django.urls import reverse
from django.utils.safestring import mark_safe
from django.views.generic import FormView

from constance import config
from django_select2.forms import Select2Widget

from aiarena.core.exceptions import MatchRequestException
from aiarena.core.models import Bot, Map, MapPool
from aiarena.core.services import match_requests, supporters


class BotWidget(Select2Widget):
    search_fields = ["name__icontains"]


class BotChoiceField(forms.ModelChoiceField):
    def label_from_instance(self, bot_object):
        str_fmt = "{0:>20} {1:>20} [{2:>20} ] {3:>20}"
        if bot_object.competition_participations.filter(active=True).exists():
            active = "✔"
        else:
            active = "✘"
        race = bot_object.plays_race
        if race.label == "T":
            race = "Terran"
        elif race.label == "P":
            race = "Protoss"
        elif race.label == "Z":
            race = "Zerg"
        elif race.label == "R":
            race = "Random"
        return str_fmt.format(active, race, bot_object.name, bot_object.user.username)


class RequestMatchForm(forms.Form):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Pre fill the map pool selection, for user convenience
        self.initial["map_pool"] = MapPool.objects.filter(id=config.MATCH_REQUESTS_PREFILL_MAP_POOL_ID).first()

    MATCHUP_TYPE_CHOICES = (
        ("specific_matchup", "Specific Matchup"),
        ("random_ladder_bot", "Random Ladder Bot"),
    )
    MATCHUP_RACE_CHOICES = (
        ("any", "Any"),
        ("T", "Terran"),
        ("Z", "Zerg"),
        ("P", "Protoss"),
    )
    MAP_SELECTION_TYPE = (
        ("map_pool", "Map Pool"),
        ("specific_map", "Specific Map"),
    )
    matchup_type = forms.ChoiceField(
        choices=MATCHUP_TYPE_CHOICES,
        widget=Select2Widget,
        required=True,
        initial="specific_matchup",
    )
    bot1 = BotChoiceField(queryset=Bot.objects.all(), required=True, widget=BotWidget)
    # hidden when matchup_type != random_ladder_bot
    matchup_race = forms.ChoiceField(choices=MATCHUP_RACE_CHOICES, widget=Select2Widget, required=False, initial="any")
    show_active_only = forms.BooleanField(label="Active Bots Only", required=False)
    # hidden when matchup_type != specific_matchup
    bot2 = BotChoiceField(
        queryset=Bot.objects.all(),
        widget=BotWidget,  # default this to required initially
        required=False,
        help_text="Author or Bot name",
    )
    map_selection_type = forms.ChoiceField(
        choices=MAP_SELECTION_TYPE, widget=Select2Widget, required=True, initial="map_pool"
    )
    map = forms.ModelChoiceField(
        queryset=Map.objects.filter(enabled=True).only("name").order_by("name"), widget=Select2Widget, required=False
    )
    map_pool = forms.ModelChoiceField(
        queryset=MapPool.objects.filter(maps__isnull=False, enabled=True).distinct().only("name").order_by("name"),
        widget=Select2Widget,
        required=False,
    )

    match_count = forms.IntegerField(min_value=1, initial=1)

    def clean_matchup_race(self):
        """If matchup_type isn't set, assume it's any"""
        return (
            "any"
            if self.cleaned_data["matchup_race"] is None or self.cleaned_data["matchup_race"] == ""
            else self.cleaned_data["matchup_race"]
        )

    def clean_bot2(self):
        """If matchup_type is specific_matchup require a bot2"""
        matchup_type = self.cleaned_data["matchup_type"]
        bot2 = self.cleaned_data["bot2"]
        if matchup_type == "specific_matchup" and bot2 is None:
            raise ValidationError("A bot2 must be specified for a specific matchup.")
        return self.cleaned_data["bot2"]

    def clean_map_pool(self):
        """If map_selection_type is map_pool require a map_pool"""
        try:
            map_selection_type = self.cleaned_data["map_selection_type"]
            map_pool = self.cleaned_data["map_pool"]
            if map_selection_type == "map_pool" and map_pool is None:
                raise ValidationError("A map pool must be specified Map Selection Type is Map Pool")
            return self.cleaned_data["map_pool"]
        except KeyError:
            raise ValidationError("Map Selection Type is required")

    def clean_map(self):
        """If map_selection_type is map require a map"""
        try:
            map_selection_type = self.cleaned_data["map_selection_type"]
            map = self.cleaned_data["map"]
            if map_selection_type == "map" and map is None:
                raise ValidationError("A map must be specified when Map Selection Type is Map.")
            return self.cleaned_data["map"]
        except KeyError:
            raise ValidationError("Map Selection Type is required")


class RequestMatch(LoginRequiredMixin, FormView):
    form_class = RequestMatchForm
    template_name = "request_match.html"

    def get_login_url(self):
        return reverse("login")

    def get_success_url(self):
        return reverse("requestmatch")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["match_request_count_left"] = match_requests.get_user_match_request_count_left(self.request.user)
        context["requested_matches_limit"] = supporters.get_requested_matches_limit(self.request.user)
        return context

    def form_valid(self, form):
        try:
            bot1 = form.cleaned_data["bot1"]
            opponent = form.cleaned_data["bot2"]
            match_count = form.cleaned_data["match_count"]
            matchup_race = form.cleaned_data["matchup_race"]
            matchup_type = form.cleaned_data["matchup_type"]
            map_selection_type = form.cleaned_data["map_selection_type"]
            map_pool = form.cleaned_data["map_pool"]
            chosen_map = form.cleaned_data["map"]

            match_list = match_requests.request_matches(
                self.request.user.websiteuser,
                bot1,
                opponent,
                match_count,
                matchup_race,
                matchup_type,
                map_selection_type,
                map_pool,
                chosen_map,
            )
            message = ""
            for match in match_list:
                message += f"<a href='{reverse('match', kwargs={'pk': match.id})}'>Match {match.id}</a> created.<br/>"
            messages.success(self.request, mark_safe(message))
            return super().form_valid(form)
        except MatchRequestException as e:
            messages.error(self.request, str(e))
            return self.render_to_response(self.get_context_data(form=form))
