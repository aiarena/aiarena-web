from datetime import timedelta

from constance import config
from django import forms
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.db import transaction, IntegrityError
from django.db.models import F, Prefetch, Count, Q
from django.shortcuts import render, redirect
from django.urls import reverse
from django.utils import timezone
from django.views import View
from django.views.generic import CreateView, ListView, UpdateView, DetailView, FormView
from private_storage.views import PrivateStorageDetailView
from rest_framework.authtoken.models import Token
from wiki.editors import getEditor
from wiki.models import ArticleRevision

from aiarena.api.arenaclient.exceptions import NoCurrentSeason
from aiarena.core.models import Bot, Result, User, Round, Match, MatchParticipation, SeasonParticipation, Season, Map
from aiarena.frontend.utils import restrict_page_range


class UserProfile(LoginRequiredMixin, DetailView):
    model = User
    redirect_field_name = 'next'
    template_name = 'profile.html'

    def get_login_url(self):
        return reverse('login')

    def get_success_url(self):
        return reverse('profile')

    def get_object(self, *args, **kwargs):
        return self.request.user

    def get_context_data(self, **kwargs):
        context = super(UserProfile, self).get_context_data(**kwargs)
        # Add in the user's bots
        context['bot_list'] = self.request.user.bots.all()
        context['max_user_bot_count'] = config.MAX_USER_BOT_COUNT
        context['max_active_per_race_bot_count'] = self.request.user.get_active_bots_per_race_limit_display()
        return context


class UserTokenDetailView(LoginRequiredMixin, DetailView):
    model = Token
    redirect_field_name = 'next'
    template_name = 'profile_token.html'
    fields = ['user', ]

    def get_login_url(self):
        return reverse('login')

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
        return redirect('profile_token')


class UserProfileUpdateForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'receive_email_comms']


class UserProfileUpdate(SuccessMessageMixin, LoginRequiredMixin, UpdateView):
    form_class = UserProfileUpdateForm
    redirect_field_name = 'next'
    template_name = 'profile_edit.html'
    success_message = "Profile saved successfully"

    def get_login_url(self):
        return reverse('login')

    def get_success_url(self):
        return reverse('profile')

    def get_object(self, *args, **kwargs):
        return self.request.user


class BotUpload(SuccessMessageMixin, LoginRequiredMixin, CreateView):
    redirect_field_name = 'next'
    template_name = 'botupload.html'
    success_message = "Bot was uploaded successfully"

    model = Bot
    fields = ['name', 'bot_zip', 'plays_race', 'type', 'active']

    def get_login_url(self):
        return reverse('login')

    def get_success_url(self):
        return reverse('botupload')

    def get_form_kwargs(self):
        # set the bot's user
        kwargs = super(BotUpload, self).get_form_kwargs()
        if kwargs['instance'] is None:
            kwargs['instance'] = Bot()
        kwargs['instance'].user = self.request.user
        return kwargs


class BotList(ListView):
    queryset = Bot.objects.all().order_by('name')
    template_name = 'bots.html'
    paginate_by = 50

    def get_context_data(self, **kwargs):
        context = super(BotList, self).get_context_data(**kwargs)

        # add the page ranges
        page_obj = context['page_obj']
        context['page_range'] = restrict_page_range(page_obj.paginator.num_pages, page_obj.number)

        return context


class BotDetail(DetailView):
    model = Bot
    template_name = 'bot.html'

    def get_context_data(self, **kwargs):
        context = super(BotDetail, self).get_context_data(**kwargs)

        results = Result.objects.filter(match__matchparticipation__bot=self.object).order_by('-created')

        # paginate the results
        page = self.request.GET.get('page', 1)
        paginator = Paginator(results, 30)
        try:
            results = paginator.page(page)
        except PageNotAnInteger:
            results = paginator.page(1)
        except EmptyPage:
            results = paginator.page(paginator.num_pages)

        # retrieve the opponent and transform the result type to be personal to this bot
        for result in results:
            result.opponent = result.match.matchparticipation_set.exclude(bot=self.object).get()
            result.me = result.match.matchparticipation_set.get(bot=self.object)

            # convert the type to be relative to this bot
            typeSuffix = ''
            if result.type in ['Player1Crash', 'Player2Crash']:
                typeSuffix = ' - Crash'
            elif result.type in ['Player1TimeOut', 'Player2TimeOut']:
                typeSuffix = ' - TimeOut'

            if result.winner is not None:

                if result.winner == self.object:
                    result.relative_type = 'Win' + typeSuffix
                else:
                    result.relative_type = 'Loss' + typeSuffix
            else:
                result.relative_type = result.type

        context['stats_bot_matchups'] = self.object.statsbotmatchups_set.all().order_by('-win_perc')
        context['rankings'] = self.object.seasonparticipation_set.all().order_by('-id')
        context['result_list'] = results
        context['results_page_range'] = restrict_page_range(paginator.num_pages, results.number)
        return context


class StandardBotUpdateForm(forms.ModelForm):
    wiki_article_content = forms.CharField(label='Bot page content', required=False, widget=getEditor().get_widget())

    class Meta:
        model = Bot
        fields = ['active', 'bot_zip', 'bot_zip_publicly_downloadable', 'bot_data',
                  'bot_data_publicly_downloadable']


class NoCurrentSeasonBotUpdateForm(forms.ModelForm):
    active = forms.BooleanField(disabled=True, required=False)
    wiki_article_content = forms.CharField(label='Bot page content', required=False, widget=getEditor().get_widget())

    class Meta:
        model = Bot
        fields = ['active', 'bot_zip', 'bot_zip_publicly_downloadable', 'bot_data', 'bot_data_publicly_downloadable']


class FrozenDataBotUpdateForm(forms.ModelForm):
    bot_data = forms.FileField(disabled=True)
    wiki_article_content = forms.CharField(label='Bot page content', required=False, widget=getEditor().get_widget())

    class Meta:
        model = Bot
        fields = ['active', 'bot_zip', 'bot_zip_publicly_downloadable', 'bot_data',
                  'bot_data_publicly_downloadable']


class NoCurrentSeasonFrozenDataBotUpdateForm(forms.ModelForm):
    active = forms.BooleanField(disabled=True)
    bot_data = forms.FileField(disabled=True)
    wiki_article_content = forms.CharField(label='Bot page content', required=False, widget=getEditor().get_widget())

    class Meta:
        model = Bot
        fields = ['active', 'bot_zip', 'bot_zip_publicly_downloadable', 'bot_data',
                  'bot_data_publicly_downloadable']


class BotUpdate(SuccessMessageMixin, LoginRequiredMixin, UpdateView):
    template_name = 'bot_edit.html'

    redirect_field_name = 'next'
    success_message = "Bot saved successfully"

    def get_queryset(self):
        return Bot.objects.filter(user=self.request.user)

    def get_login_url(self):
        return reverse('login')

    def get_success_url(self):
        return reverse('bot_edit', kwargs={'pk': self.object.pk})

    # change the available fields based upon whether the bot_data is available for editing or not
    # and whether there's a current season
    def get_form_class(self):
        if self.object.bot_data_is_currently_frozen():
            try:
                Season.get_current_season()
                return FrozenDataBotUpdateForm
            except NoCurrentSeason:
                return NoCurrentSeasonFrozenDataBotUpdateForm
        else:
            try:
                Season.get_current_season()
                return StandardBotUpdateForm
            except NoCurrentSeason:
                return NoCurrentSeasonBotUpdateForm

    def get_form(self, form_class=None):
        """Return an instance of the form to be used in this view."""

        if form_class is None:
            form_class = self.get_form_class()

        # load the wiki article content as the initial value
        wiki_article_content = self.object.wiki_article.current_revision.content
        kwargs = self.get_form_kwargs()
        kwargs['initial']['wiki_article_content'] = wiki_article_content
        return form_class(**kwargs)

    def form_valid(self, form):
        """Create a new article revision for the bot wiki page when the form is valid"""

        # If the article content is different, add a new revision
        if form.instance.wiki_article.current_revision.content != form.cleaned_data['wiki_article_content']:
            revision = ArticleRevision()
            revision.inherit_predecessor(form.instance.wiki_article)
            revision.title = form.instance.name
            revision.content = form.cleaned_data['wiki_article_content']
            # revision.user_message = form.cleaned_data['summary']
            revision.deleted = False
            revision.set_from_request(self.request)
            form.instance.wiki_article.add_revision(revision)
        return super(BotUpdate, self).form_valid(form)


class AuthorList(ListView):
    queryset = User.objects.filter(is_active=1, type='WEBSITE_USER').order_by('username')
    template_name = 'authors.html'


class AuthorDetail(DetailView):
    queryset = User.objects.filter(is_active=1, type='WEBSITE_USER')
    template_name = 'author.html'
    context_object_name = 'author'  # change the context name to avoid overriding the current user oontext object

    def get_context_data(self, **kwargs):
        context = super(AuthorDetail, self).get_context_data(**kwargs)
        context['bot_list'] = Bot.objects.filter(user_id=self.object.id).order_by('-created')
        return context


# Using a ListView, which has automated behaviour for displaying a list of models
class Ranking(ListView):
    # If we wanted all the bots, we could just set this and, because we're extending a ListView, it would
    # understand to get all the Bots, which could be referenced as "seasonparticipation_list" in the template.
    # model = SeasonParticipation

    # Instead, because we want to filter the bots, we define queryset,
    # which is also referenced as "seasonparticipation_list" in the template.
    def get_queryset(self):
        try:
            return SeasonParticipation.objects.filter(season=Season.get_current_season()).order_by(
                '-elo').prefetch_related('bot')
        except NoCurrentSeason:
            return SeasonParticipation.objects.none()

    # If we didn't set this, the ListView would default to searching for a template at <module>/<modelname>_list.html
    # In this case, that would be "core/seasonparticipation_list.html"
    template_name = 'ranking.html'

    def get_context_data(self, **kwargs):
        context = super(Ranking, self).get_context_data(**kwargs)
        try:
            season = Season.get_current_season()
            context['current_season_name'] = season.name
        except NoCurrentSeason:
            pass
        return context


class Results(ListView):
    queryset = Result.objects.all().order_by('-created').prefetch_related(
        Prefetch('winner'),
        Prefetch('match__matchparticipation_set', MatchParticipation.objects.all().prefetch_related('bot'),
                 to_attr='participants'))
    template_name = 'results.html'
    paginate_by = 50

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # add the page ranges
        page_obj = context['page_obj']
        context['page_range'] = restrict_page_range(page_obj.paginator.num_pages, page_obj.number)

        return context


class ArenaClients(ListView):
    queryset = User.objects.annotate(
        matches_1hr=Count('result', distinct=True, filter=Q(match__result__created__gte=timezone.now() - timedelta(hours=1))),
    ).annotate(matches_24hr=Count('result', distinct=True, filter=Q(match__result__created__gte=timezone.now() - timedelta(hours=24))),
    ).filter(type='ARENA_CLIENT').order_by('username')
    template_name = 'arenaclients.html'


class ArenaClient(DetailView):
    queryset = User.objects.filter(type='ARENA_CLIENT')
    template_name = 'arenaclient.html'
    context_object_name = 'arenaclient'  # change the context name to avoid overriding the current user oontext object

    def get_context_data(self, **kwargs):
        context = super(ArenaClient, self).get_context_data(**kwargs)

        results = Result.objects.filter(match__assigned_to=self.object).order_by('-created').prefetch_related(
            Prefetch('winner'),
            Prefetch('match__matchparticipation_set', MatchParticipation.objects.all().prefetch_related('bot'),
                     to_attr='participants'))

        context['ac_match_count_1h'] = Result.objects.filter(match__assigned_to=self.object,
                                                          created__gte=timezone.now() - timedelta(hours=1)).count()
        context['ac_match_count_24h'] = Result.objects.filter(match__assigned_to=self.object,
                                                           created__gte=timezone.now() - timedelta(hours=24)).count()
        context['ac_match_count'] = results.count()

        # paginate the results
        page = self.request.GET.get('page', 1)
        paginator = Paginator(results, 30)
        try:
            results = paginator.page(page)
        except PageNotAnInteger:
            results = paginator.page(1)
        except EmptyPage:
            results = paginator.page(paginator.num_pages)

        context['result_list'] = results
        context['results_page_range'] = restrict_page_range(paginator.num_pages, results.number)
        return context


class RoundDetail(DetailView):
    model = Round
    template_name = 'round.html'


class BotZipDownloadView(PrivateStorageDetailView):
    model = Bot
    model_file_field = 'bot_zip'

    content_disposition = 'attachment'

    def get_content_disposition_filename(self, private_file):
        return '{0}.zip'.format(private_file.parent_object.name)

    def can_access_file(self, private_file):
        user = private_file.request.user
        # Allow if staff, the owner of the file, or the file is marked as publicly downloadable
        return user.is_authenticated and user.is_staff or private_file.parent_object.user == user or private_file.parent_object.bot_zip_publicly_downloadable


class BotDataDownloadView(PrivateStorageDetailView):
    model = Bot
    model_file_field = 'bot_data'

    content_disposition = 'attachment'

    def get_content_disposition_filename(self, private_file):
        return '{0}_data.zip'.format(private_file.parent_object.name)

    def can_access_file(self, private_file):
        user = private_file.request.user
        # Allow if staff, the owner of the file, or the file is marked as publicly downloadable
        return user.is_authenticated and user.is_staff or private_file.parent_object.user == user or private_file.parent_object.bot_data_publicly_downloadable


class MatchLogDownloadView(PrivateStorageDetailView):
    model = MatchParticipation
    model_file_field = 'match_log'

    content_disposition = 'attachment'

    def get_content_disposition_filename(self, private_file):
        return '{0}_{1}_log.zip'.format(private_file.parent_object.bot.name, private_file.parent_object.id)

    def can_access_file(self, private_file):
        user = private_file.request.user
        # Allow if staff or the owner of the file
        return user.is_authenticated and user.is_staff or private_file.parent_object.bot.user == user


class Index(ListView):
    def get_queryset(self):
        try:
            return SeasonParticipation.objects.filter(season=Season.get_current_season(), bot__active=1).order_by(
                '-elo')[
                   :10].prefetch_related('bot')  # top 10 bots
        except NoCurrentSeason:
            return SeasonParticipation.objects.none()

    template_name = 'index.html'


class MatchQueue(View):
    def get(self, request):
        # Matches without a round are requested ones
        requested_matches = Match.objects.filter(round__isnull=True, result__isnull=True).order_by(
            F('started').asc(nulls_last=True), F('id').asc()).prefetch_related(
            Prefetch('map'),
            Prefetch('matchparticipation_set', MatchParticipation.objects.all().prefetch_related('bot'),
                     to_attr='participants'))

        # Matches with a round
        rounds = Round.objects.filter(complete=False).order_by(F('id').asc())
        for round in rounds:
            round.matches = Match.objects.filter(round_id=round.id, result__isnull=True).order_by(
                F('started').asc(nulls_last=True), F('id').asc()).prefetch_related(
                Prefetch('map'),
                Prefetch('matchparticipation_set', MatchParticipation.objects.all().prefetch_related('bot'),
                         to_attr='participants'))

        context = {'round_list': rounds, 'requested_matches': requested_matches}
        return render(request, 'match_queue.html', context)


class MatchDetail(DetailView):
    model = Match
    template_name = 'match.html'


class SeasonList(ListView):
    queryset = Season.objects.all().order_by('-id')
    template_name = 'seasons.html'


class SeasonDetail(DetailView):
    model = Season
    template_name = 'season.html'

    def get_context_data(self, **kwargs):
        context = super(SeasonDetail, self).get_context_data(**kwargs)
        context['round_list'] = Round.objects.filter(season_id=self.object.id).order_by('-id')
        context['rankings'] = SeasonParticipation.objects.filter(season_id=self.object.id).order_by('-elo')
        return context


class RequestMatchForm(forms.Form):
    bot1 = forms.ModelChoiceField(queryset=Bot.objects.all(), empty_label=None, required=True)
    bot2 = forms.ModelChoiceField(queryset=Bot.objects.all(), empty_label='Random', required=False)
    map = forms.ModelChoiceField(queryset=Map.objects.filter(active=True), empty_label='Random', required=False)

    def request_match(self, user):
        Match.request_bot_match(self.cleaned_data['bot1'], self.cleaned_data['bot2'], self.cleaned_data['map'], user)


class RequestMatch(LoginRequiredMixin, SuccessMessageMixin, FormView):
    form_class = RequestMatchForm
    template_name = 'request_match.html'
    success_message = "Match requested"

    def get_login_url(self):
        return reverse('login')

    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        # If not staff, only allow requesting games against this user's bots
        if not self.request.user.is_staff:
            form.fields['bot1'].queryset=Bot.objects.filter(user=self.request.user)
        return form

    def get_success_url(self):
        return reverse('requestmatch')

    def form_valid(self, form):
        form.request_match(self.request.user)
        return super().form_valid(form)
