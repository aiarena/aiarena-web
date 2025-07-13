from django import forms
from django.db.models import F, Prefetch, Q
from django.shortcuts import redirect
from django.utils.safestring import mark_safe
from django.views.generic import DetailView

import django_filters as filters
import django_tables2 as tables
from django_filters.widgets import RangeWidget
from django_tables2 import LazyPaginator, RequestConfig

from aiarena.core.d_utils import filter_tags
from aiarena.core.models import Bot, Competition, MatchParticipation, RelativeResult, Trophy
from aiarena.core.models.bot_race import BotRace
from aiarena.core.s3_helpers import get_file_url_s3_hack
from aiarena.frontend.templatetags.core_filters import format_elo_change, result_color_class, step_time_color
from aiarena.frontend.templatetags.url_utils import get_bot_html_link, get_bot_truncated_html_link


class FileURLColumn(tables.URLColumn):
    """File URLs are incorrect without this"""

    def get_url(self, value):
        return value.url


class MatchFileURLColumn(tables.URLColumn):
    """
    File URLs are incorrect without this
    This is a quick hack to insert the S3 content disposition logic.
    """

    def get_url(self, value):
        file_name = f"{value.instance.me.bot.name}_{value.instance.me.id}_log.zip"
        return get_file_url_s3_hack(value, file_name)


class BotResultTable(tables.Table):
    # Settings for individual columns
    # match could be a LinkColumn, but used ".as_html_link" since that is being used elsewhere.
    match = tables.Column(verbose_name="ID")
    started = tables.DateTimeColumn(format="d N y, H:i", verbose_name="Date")
    result = tables.Column(attrs={"td": {"class": lambda value: result_color_class(value)}})
    result_cause = tables.Column(verbose_name="Cause")
    elo_change = tables.Column(verbose_name="+/-")
    avg_step_time = tables.Column(
        verbose_name="Avg Step(ms)", attrs={"td": {"style": lambda value: f"color: {step_time_color(value)};'"}}
    )
    game_time_formatted = tables.Column(verbose_name="Duration")
    replay_file = FileURLColumn(verbose_name="Replay", orderable=False, attrs={"a": {"class": "file-link"}})
    match_log = MatchFileURLColumn(verbose_name="Log", orderable=False, attrs={"a": {"class": "file-link"}})
    match__tags = tables.ManyToManyColumn(verbose_name="Tags")

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop("user", None)
        self.tags_by_all_value = kwargs.pop("tags_by_all_value", False)
        super().__init__(*args, **kwargs)

    # Settings for the Table
    class Meta:
        attrs = {
            "class": "row-hover-highlight",
            "style": "text-align: center;",
            "thead": {"style": "height: 35px;"},
        }
        model = RelativeResult
        fields = (
            "match",
            "started",
            "opponent",
            "result",
            "result_cause",
            "elo_change",
            "avg_step_time",
            "game_time_formatted",
            "replay_file",
            "match_log",
            "match__tags",
        )

    # Custom Column Rendering
    def render_match(self, value):
        return get_bot_html_link(value)

    def render_opponent(self, value):
        return get_bot_truncated_html_link(value.bot)

    def render_elo_change(self, record, value):
        return "--" if record.match.requested_by else format_elo_change(value)

    def render_avg_step_time(self, value):
        try:
            return int(float(value) * 1000)
        except ValueError:
            return "--"

    def render_replay_file(self, value):
        return "Download"

    def render_match_log(self, value):
        return "Download"

    def render_match__tags(self, value):
        tag_str = ""
        user_tags = value.filter(user=self.user) if self.user.is_authenticated else []
        if len(user_tags) > 0:
            tag_str += "My Tags:\n" if self.tags_by_all_value else ""
            tag_str += ", ".join(str(mt.tag) for mt in user_tags.order_by("tag__name"))

        others_tags_dict = {}
        if self.tags_by_all_value:
            # Distinct Tag Names
            others_tags = value.exclude(user=self.user) if self.user.is_authenticated else value.all()
            others_tags_dict = {str(mt.tag): None for mt in others_tags.order_by("tag__name")}
            if len(others_tags) > 0:
                tag_str += ("\n\n" if len(tag_str) > 0 else "") + "Other's Tags:\n"
                tag_str += ", ".join(t for t in others_tags_dict)

        if len(tag_str) > 0:
            return mark_safe(f'<abbr title="{tag_str}">Hover<{len(user_tags) + len(others_tags_dict)}></abbr>')
        else:
            return "—"


class RelativeResultFilter(filters.FilterSet):
    MATCH_TYPES = (
        ("competition", "Competition"),
        ("requested", "Requested"),
    )

    opponent = filters.CharFilter(label="Opponent", field_name="opponent__bot__name", lookup_expr="icontains")
    race = filters.ModelChoiceFilter(
        label="Race",
        queryset=BotRace.objects.all(),
        field_name="opponent__bot__plays_race",
        widget=forms.Select(attrs={"style": "width: 100%"}),
    )
    result = filters.ChoiceFilter(label="Result", choices=MatchParticipation.RESULT_TYPES[1:])
    result_cause = filters.ChoiceFilter(label="Cause", choices=MatchParticipation.CAUSE_TYPES)
    avg_step_time = filters.RangeFilter(
        label="Average Step Time", method="filter_avg_step_time", widget=RangeWidget(attrs={"size": 4})
    )
    match_type = filters.ChoiceFilter(label="Match Type", choices=MATCH_TYPES, method="filter_match_types")
    competition = filters.ModelChoiceFilter(
        label="Competition",
        queryset=Competition.objects.all(),
        field_name="match__round__competition",
        widget=forms.Select(attrs={"style": "width: 100%"}),
    )
    map = filters.CharFilter(label="Map", field_name="match__map__name", lookup_expr="icontains")
    tags = filters.CharFilter(
        label="Tags",
        method="filter_tags",
        widget=forms.TextInput(attrs={"data-role": "tagsinput", "style": "width: 100%"}),
    )
    # Just need the widget, value is passed on init to be used in tag filter
    tags_by_all = filters.BooleanFilter(label="Search Everyones Tags", method="no_filter", widget=forms.CheckboxInput)
    tags_partial_match = filters.BooleanFilter(
        label="Partially Match Tags", method="no_filter", widget=forms.CheckboxInput
    )

    class Meta:
        model = RelativeResult
        fields = ["opponent__bot__name", "opponent__bot__plays_race", "result", "result_cause", "avg_step_time", "tags"]

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop("user", None)
        self.tags_by_all_value = kwargs.pop("tags_by_all_value", False)
        self.tags_partial_match_value = kwargs.pop("tags_partial_match_value", False)
        super().__init__(*args, **kwargs)
        # Set Widget initial value based on passed value
        self.form.fields["tags_by_all"].widget.attrs = {"checked": self.tags_by_all_value}
        self.form.fields["tags_partial_match"].widget.attrs = {"checked": self.tags_partial_match_value}

    # Custom filter to match scale
    def filter_avg_step_time(self, queryset, name, value):
        if value:
            if value.start is not None and value.stop is not None:
                return queryset.filter(avg_step_time__range=[value.start / 1000, value.stop / 1000])
            elif value.start is not None:
                return queryset.filter(avg_step_time__gte=value.start / 1000)
            elif value.stop is not None:
                return queryset.filter(avg_step_time__lte=value.stop / 1000)
        return queryset

    def filter_match_types(self, queryset, name, value):
        if value == self.MATCH_TYPES[0][0]:
            return queryset.filter(match__requested_by__isnull=True)
        elif value == self.MATCH_TYPES[1][0]:
            return queryset.filter(match__requested_by__isnull=False)
        return queryset

    def filter_tags(self, qs, name, value):
        # An unauthenticated user will have no tags
        if not self.user.is_authenticated and not self.tags_by_all_value:
            return qs.none()

        if not self.tags_by_all_value:
            value = str(self.user.id) + "|" + value

        if self.tags_partial_match_value:
            return filter_tags(qs, value, "match__tags__tag__name", "icontains", "match__tags__user")
        else:
            return filter_tags(qs, value, "match__tags__tag__name", "iexact", "match__tags__user")

    def no_filter(self, queryset, name, value):
        return queryset


class BotDetail(DetailView):
    model = Bot
    template_name = "bot.html"

    def dispatch(self, request, *args, **kwargs):
        # This aims to prevent crawlers from overloading our database -
        # they're scanning high page numbers with weird sorts
        # while pretending to be actual users (UserAgent looks like a browser)
        page_number = int(self.request.GET.get("page", "1"))
        if page_number > 1 and not request.user.is_authenticated:
            return redirect("login")
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Create Table
        results_qs = (
            RelativeResult.objects.select_related("match", "me__bot", "opponent__bot")
            .defer("me__bot__bot_data")
            .filter(me__bot=self.object)
            .order_by("-started")
        )

        # specially construct the url, in case we're using S3
        context["bot_zip_url"] = self.get_bot_zip_url()
        context["bot_zip_data_url"] = self.get_bot_zip_data_url()

        # Get tags_by_all and remove it from params to prevent errors
        params = self.request.GET.copy()
        tags_by_all = params.pop("tags_by_all")[0] == "on" if "tags_by_all" in params else False
        tags_partial_match = params.pop("tags_partial_match")[0] == "on" if "tags_partial_match" in params else False
        # Run filters, create table
        result_filter = RelativeResultFilter(
            params,
            queryset=results_qs,
            user=self.request.user,
            tags_by_all_value=tags_by_all,
            tags_partial_match_value=tags_partial_match,
        )
        result_table = BotResultTable(
            data=result_filter.qs.prefetch_related(Prefetch("match__tags")),
            user=self.request.user,
            tags_by_all_value=tags_by_all,
        )
        result_table.exclude = []
        # Exclude log column if not staff or user
        if not (self.request.user == self.object.user or self.request.user.is_staff):
            result_table.exclude.append("match_log")
        # Update table based on request information
        RequestConfig(self.request, paginate={"per_page": 30, "paginator_class": LazyPaginator}).configure(result_table)
        context["results_table"] = result_table
        context["filter"] = result_filter

        context["bot_trophies"] = Trophy.objects.filter(bot=self.object)
        context["rankings"] = self.object.competition_participations.all().select_related("competition").order_by("-id")
        context["queued_or_in_progress"] = (
            MatchParticipation.objects.only("match")
            .filter(
                Q(match__requested_by__isnull=False) | Q(match__assigned_to__isnull=False),
                match__result=None,
                bot=self.object,
            )
            .order_by(F("match__started").asc(nulls_last=True), F("match__id").asc())
            .prefetch_related(
                Prefetch("match__map"),
                Prefetch(
                    "match__matchparticipation_set",
                    MatchParticipation.objects.all().prefetch_related("bot"),
                    to_attr="participants",
                ),
            )
        )

        return context

    def get_bot_zip_url(self):
        return get_file_url_s3_hack(self.object.bot_zip, f"{self.object.name}.zip")

    def get_bot_zip_data_url(self):
        return get_file_url_s3_hack(self.object.bot_data, f"{self.object.name}_data.zip")
