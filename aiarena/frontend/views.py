from datetime import timedelta

from constance import config
from discord_bind.models import DiscordUser
from django import forms
from django.http import Http404
from django_select2.forms import Select2Widget, ModelSelect2Widget
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.core.exceptions import ValidationError
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.db import transaction, IntegrityError
from django.db.models import F, Prefetch, Q
from django.shortcuts import render, redirect
from django.urls import reverse
from django.utils import timezone
from django.utils.safestring import mark_safe
from django.views import View
from django.views.generic import CreateView, ListView, UpdateView, DetailView, FormView, TemplateView, DeleteView
from private_storage.views import PrivateStorageDetailView
from rest_framework.authtoken.models import Token
from wiki.editors import getEditor
from wiki.models import ArticleRevision

from aiarena.api.arenaclient.exceptions import NoCurrentlyAvailableCompetitions
from aiarena.core.api.ladders import Ladders
from aiarena.core.api import Matches
from aiarena.core.models import Bot, Result, User, Round, Match, MatchParticipation, CompetitionParticipation, Competition, Map, \
    ArenaClient, News
from aiarena.core.models import Trophy
from aiarena.core.models.relative_result import RelativeResult
from aiarena.frontend.utils import restrict_page_range
from aiarena.patreon.models import PatreonAccountBind

def project_finance(request):
    return render(request, template_name='finance.html')

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
        context['max_active_per_race_bot_count'] = self.request.user.get_active_bots_limit_display()
        context['requested_matches'] = Match.objects.filter(requested_by=self.object, result__isnull=True).order_by(
            F('started').asc(nulls_last=True), F('id').asc()).prefetch_related(
            Prefetch('map'),
            Prefetch('matchparticipation_set', MatchParticipation.objects.all().prefetch_related('bot'),
                     to_attr='participants'))
        return context

    @transaction.atomic
    def post(self, request, *args, **kwargs):
        match_ids = request.POST.getlist('match_selection')
        # Get and cancel requested matches
        matches = Match.objects.filter(pk__in=match_ids, requested_by=self.request.user, result__isnull=True, assigned_to__isnull=True)
        if matches:
            message = "Matches " if len(matches)>1 else "Match "
            for match in matches:
                result = match.cancel(request.user)
                if result == Match.CancelResult.MATCH_DOES_NOT_EXIST:  # should basically not happen, but just in case
                    raise Exception('Match "%s" does not exist' % match.id)
                elif result == Match.CancelResult.RESULT_ALREADY_EXISTS:
                    raise Exception('A result already exists for match "%s"' % match.id)
                message += f"<a href='{reverse('match', kwargs={'pk': match.id})}'>{match.id}</a>, "
            message = message[:-2] + " cancelled."
            messages.success(self.request, mark_safe(message))
        else:
            messages.error(self.request, mark_safe("No matches were found for cancellation."))
        return redirect('profile')


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


class UnlinkDiscordView(LoginRequiredMixin, DeleteView):
    model = DiscordUser
    template_name = 'discord/confirm_unlink.html'

    def get_login_url(self):
        return reverse('login')

    def get_success_url(self):
        return reverse('profile')

    def get_object(self, *args, **kwargs):
        return self.request.user.discord_user


class UnlinkPatreonView(LoginRequiredMixin, DeleteView):
    model = PatreonAccountBind
    template_name = 'patreon/confirm_unlink.html'

    def get_login_url(self):
        return reverse('login')

    def get_success_url(self):
        return reverse('profile')

    def get_object(self, *args, **kwargs):
        return self.request.user.patreonaccountbind


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


class BotUploadForm(forms.ModelForm):
    class Meta:
        model = Bot
        fields = ['name', 'bot_zip', 'bot_data_enabled', 'plays_race', 'type', ]


class BotUpload(SuccessMessageMixin, LoginRequiredMixin, CreateView):
    form_class = BotUploadForm
    redirect_field_name = 'next'
    template_name = 'botupload.html'
    success_message = "Bot was uploaded successfully"

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

    def form_valid(self, form):
        if config.BOT_UPLOADS_ENABLED:
            return super().form_valid(form)
        else:
            messages.error(self.request, "Sorry. Requested matches are currently disabled.")
            return self.render_to_response(self.get_context_data(form=form))


class BotList(ListView):
    queryset = Bot.objects.all().only('name', 'plays_race', 'type', 'user__username', 'user__type')\
        .select_related('user').order_by('name')
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

        results = RelativeResult.objects.select_related('match', 'me__bot', 'opponent__bot').defer("me__bot__bot_data")\
            .filter(me__bot=self.object).order_by('-created')

        # paginate the results
        page = self.request.GET.get('page', 1)
        paginator = Paginator(results, 30)
        try:
            results = paginator.page(page)
        except PageNotAnInteger:
            results = paginator.page(1)
        except EmptyPage:
            results = paginator.page(paginator.num_pages)

        context['bot_trophies'] = Trophy.objects.filter(bot=self.object)
        context['rankings'] = self.object.competition_participations.all().order_by('-id')
        context['match_participations'] = MatchParticipation.objects.only("match")\
            .filter(Q(match__requested_by__isnull=False)|Q(match__assigned_to__isnull=False), bot=self.object, match__result__isnull=True)\
            .order_by(F('match__started').asc(nulls_last=True), F('match__id').asc())\
            .prefetch_related(
                Prefetch('match__map'),
                Prefetch('match__matchparticipation_set', MatchParticipation.objects.all().prefetch_related('bot'), to_attr='participants'))
        context['result_list'] = results
        context['results_page_range'] = restrict_page_range(paginator.num_pages, results.number)
        return context


class BotCompetitionStatsDetail(DetailView):
    model = CompetitionParticipation
    template_name = 'bot_competition_stats.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['competition_bot_matchups'] = self.object.competition_matchup_stats.filter(
            opponent__competition=context['competitionparticipation'].competition).order_by('-win_perc').distinct()
        context['updated'] = context['competition_bot_matchups'][0].updated
        return context



class BotUpdateForm(forms.ModelForm):
    """
    Standard form for updating a bot
    """
    wiki_article_content = forms.CharField(label='Bot page content', required=False, widget=getEditor().get_widget())

    def __init__(self, *args, **kwargs, ):
        super().__init__(*args, **kwargs)

        # change the available fields based upon whether the bot_data is available for editing or not
        # and whether there's a current competition
        if self.instance.bot_data_is_currently_frozen():
            self.fields['bot_data'].disabled = True


    class Meta:
        model = Bot
        fields = ['bot_zip', 'bot_zip_publicly_downloadable', 'bot_data',
                  'bot_data_publicly_downloadable', 'bot_data_enabled']


class BotUpdate(SuccessMessageMixin, LoginRequiredMixin, UpdateView):
    template_name = 'bot_edit.html'
    form_class = BotUpdateForm

    redirect_field_name = 'next'
    success_message = "Bot saved successfully"

    def get_queryset(self):
        return Bot.objects.filter(user=self.request.user)

    def get_login_url(self):
        return reverse('login')

    def get_success_url(self):
        return reverse('bot_edit', kwargs={'pk': self.object.pk})

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


class CompetitionParticipationForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        bot_id = kwargs.pop('bot_id')
        super().__init__(*args, **kwargs)
        self.fields['competition'].queryset = Competition.objects.exclude(participations__bot_id=bot_id)

    class Meta:
        model = CompetitionParticipation
        fields = ['competition', ]


class CompetitionParticipationList(SuccessMessageMixin, LoginRequiredMixin, CreateView):
    template_name = 'bot_competitions.html'
    form_class = CompetitionParticipationForm

    redirect_field_name = 'next'
    success_message = "Competition joined."

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['competitionparticipation_list'] = CompetitionParticipation.objects.filter(bot_id=self.kwargs['pk'])

        try:
            context['bot'] = Bot.objects.get(id=self.kwargs['pk'], user=self.request.user)
        except Bot.DoesNotExist:
            # avoid users accessing another user's bot
            raise Http404("No bot found matching the query")

        return context

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs.update({'bot_id': self.kwargs['pk']})

        # set the associated bot
        if kwargs['instance'] is None:
            kwargs['instance'] = CompetitionParticipation()
        kwargs['instance'].bot = Bot.objects.get(pk=self.kwargs['pk'])
        return kwargs

    def get_login_url(self):
        return reverse('login')

    def get_success_url(self):
        return reverse('bot_competitions', kwargs={'pk': self.object.bot_id})


class CompetitionParticipationUpdate(SuccessMessageMixin, LoginRequiredMixin, UpdateView):
    template_name = 'bot_competitionparticipation_edit.html'
    model = CompetitionParticipation
    fields = ['active',]

    redirect_field_name = 'next'
    success_message = "Competition participation saved."

    def get_login_url(self):
        return reverse('login')

    def get_success_url(self):
        return reverse('bot_competitions', kwargs={'pk': self.kwargs['bot_id']})

class AuthorList(ListView):
    queryset = User.objects.filter(is_active=1, type='WEBSITE_USER').order_by('username')
    template_name = 'authors.html'


class AuthorDetail(DetailView):
    queryset = User.objects.filter(is_active=1, type='WEBSITE_USER')
    template_name = 'author.html'
    context_object_name = 'author'  # change the context name to avoid overriding the current user oontext object

    def get_context_data(self, **kwargs):
        context = super(AuthorDetail, self).get_context_data(**kwargs)
        context['bot_list'] = Bot.objects.select_related('user').filter(user_id=self.object.id).order_by('-created')
        return context


class Results(ListView):
    queryset = Result.objects.all().order_by('-created').prefetch_related(
        Prefetch('winner'),
        Prefetch('match__requested_by'),
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
    queryset = ArenaClient.objects.filter(is_active=True)
    # todo: why doesn't this work?
    # queryset = User.objects.filter(type='ARENA_CLIENT').annotate(
    #     matches_1hr=Count('submitted_results', filter=Q(submitted_results__created__gte=timezone.now() - timedelta(hours=1))),
    #     matches_24hr=Count('submitted_results',filter=Q(match__result__created__gte=timezone.now() - timedelta(hours=24))),
    #            ).order_by('username')
    template_name = 'arenaclients.html'

    def get_context_data(self, **kwargs):
        for arenaclient in self.object_list:
            arenaclient.matches_1hr = Result.objects.filter(match__assigned_to=arenaclient,
                                                            created__gte=timezone.now() - timedelta(
                                                                hours=1)).count()
            arenaclient.matches_24hr = Result.objects.filter(match__assigned_to=arenaclient,
                                                             created__gte=timezone.now() - timedelta(
                                                                 hours=24)).count()
        return super().get_context_data(**kwargs)


class ArenaClientView(DetailView):
    queryset = User.objects.filter(type='ARENA_CLIENT')
    template_name = 'arenaclient.html'
    context_object_name = 'arenaclient'  # change the context name to avoid overriding the current user oontext object

    def get_context_data(self, **kwargs):
        context = super(ArenaClientView, self).get_context_data(**kwargs)

        context['assigned_matches_list'] = Match.objects.filter(assigned_to=self.object,
                                                                result__isnull=True).prefetch_related(
            Prefetch('matchparticipation_set', MatchParticipation.objects.all().prefetch_related('bot'),
                     to_attr='participants'))

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
            comp = Competition.objects.get(id=1)
            if Round.objects.filter(competition=comp).count() > 0:
                return Ladders.get_competition_ranked_participants(
                    comp, amount=10).prefetch_related(
                    Prefetch('bot', queryset=Bot.objects.all().only('user_id', 'name')),
                    Prefetch('bot__user', queryset=User.objects.all().only('patreon_level')))  # top 10 bots
            else:
                return CompetitionParticipation.objects.none()
        except NoCurrentlyAvailableCompetitions:
            return CompetitionParticipation.objects.none()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # newly created bots have almost the same update time as its creation time
        events = Bot.objects.select_related('user').only('user', 'name', 'created').order_by('-bot_zip_updated')[:10]
        for event in events:
            # if these are within a second, then the bot was created, not updated
            event.is_created_event = (event.bot_zip_updated - event.created).seconds <= 1
        context['events'] = events
        context['news'] = News.objects.all().order_by('-created')

        return context

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
            round.matches = Match.objects.filter(round_id=round.id, result__isnull=True).select_related('map').order_by(
                F('started').asc(nulls_last=True), F('id').asc()).prefetch_related(
                Prefetch('matchparticipation_set', MatchParticipation.objects.all().prefetch_related('bot'),
                         to_attr='participants'))

        context = {'round_list': rounds, 'requested_matches': requested_matches}
        return render(request, 'match_queue.html', context)


class MatchDetail(DetailView):
    model = Match
    template_name = 'match.html'


class CompetitionList(ListView):
    queryset = Competition.objects.all().order_by('-id')
    template_name = 'competitions.html'


class CompetitionDetail(DetailView):
    model = Competition
    template_name = 'competition.html'

    def get_context_data(self, **kwargs):
        context = super(CompetitionDetail, self).get_context_data(**kwargs)
        context['round_list'] = Round.objects.filter(competition_id=self.object.id).order_by('-id')
        context['rankings'] = Ladders.get_competition_ranked_participants(self.object).prefetch_related(
            Prefetch('bot', queryset=Bot.objects.all().only('plays_race', 'user_id', 'name', 'type')),
            Prefetch('bot__user', queryset=User.objects.all().only('patreon_level', 'username','type')))
        context['rankings'].count = len(context['rankings'])
        return context


class BotWidget(Select2Widget):
    search_fields = [
            "name__icontains"
    ]


class BotChoiceField(forms.ModelChoiceField):
    def label_from_instance(self, bot_object):
        str_fmt = "{0:>20} {1:>20} [{2:>20} ] {3:>20}"
        if bot_object.competition_participations.filter(active=True).exists():
            active = '✔'
        else:
            active = '✘'
        race = bot_object.plays_race
        if race == 'T':
            race = 'Terran'
        elif race == 'P':
            race = 'Protoss'
        elif race == 'Z':
            race = 'Zerg'
        elif race == 'R':
            race = 'Random'
        return str_fmt.format(active, race, bot_object.name,  bot_object.user.username)


class RequestMatchForm(forms.Form):

    MATCHUP_TYPE_CHOICES = (
        ('specific_matchup', 'Specific Matchup'),
        ('random_ladder_bot', 'Random Ladder Bot'),
    )
    MATCHUP_RACE_CHOICES = (
        ('any', 'Any'),
        ('T', 'Terran'),
        ('Z', 'Zerg'),
        ('P', 'Protoss'),
    )
    matchup_type = forms.ChoiceField(choices=MATCHUP_TYPE_CHOICES,
                                     widget=Select2Widget,
                                     required=True, initial='specific_matchup',
                                     )
    bot1 = BotChoiceField(queryset=Bot.objects.all(), required=True,
                                  widget=BotWidget)
    # hidden when matchup_type != random_ladder_bot
    matchup_race = forms.ChoiceField(choices=MATCHUP_RACE_CHOICES,
                                     widget=Select2Widget,
                                     required=False, initial='any')
    # hidden when matchup_type != specific_matchup
    bot2 = BotChoiceField(queryset=Bot.objects.all(),
                                  widget=BotWidget,  # default this to required initially
                                  required=False, help_text="Author or Bot name")
    map = forms.ModelChoiceField(queryset=Map.objects.only('name').order_by('name'),
                                 empty_label='Random Ladder Map', widget=Select2Widget,
                                 required=False)

    match_count = forms.IntegerField(min_value=1, initial=1)

    def clean_matchup_race(self):
        """If matchup_type isn't set, assume it's any"""
        return 'any' if self.cleaned_data['matchup_race'] is None or self.cleaned_data['matchup_race'] == '' \
            else self.cleaned_data['matchup_race']

    def clean_bot2(self):
        """If matchup_type is specific_matchup require a bot2"""
        matchup_type = self.cleaned_data['matchup_type']
        bot2 = self.cleaned_data['bot2']
        if matchup_type == 'specific_matchup' and bot2 is None:
            raise ValidationError("A bot2 must be specified for a specific matchup.")
        return self.cleaned_data['bot2']

    # todo: validate form


class RequestMatch(LoginRequiredMixin, FormView):
    form_class = RequestMatchForm
    template_name = 'request_match.html'

    def get_login_url(self):
        return reverse('login')

    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        # If not staff, only allow requesting games against this user's bots
        if not self.request.user.is_staff and not self.request.user.can_request_games_for_another_authors_bot:
            form.fields['bot1'].queryset = Bot.objects.filter(user=self.request.user)
        return form

    def get_success_url(self):
        return reverse('requestmatch')

    def form_valid(self, form):
        if config.ALLOW_REQUESTED_MATCHES:
            if form.cleaned_data['bot1'] != form.cleaned_data['bot2']:
                if self.request.user.match_request_count_left >= form.cleaned_data['match_count']:

                    with transaction.atomic():  # do this all in one commit
                        match_list = []
                        if form.cleaned_data['matchup_type'] == 'random_ladder_bot':
                            bot1 = form.cleaned_data['bot1']

                            for _ in range(0, form.cleaned_data['match_count']):
                                bot2 = bot1.get_random_active_excluding_self() if form.cleaned_data['matchup_race'] == 'any' \
                                    else bot1.get_random_active_excluding_self(plays_race=form.cleaned_data['matchup_race'])

                                if bot2 is None:
                                    messages.error(self.request, "No opponents of that type could be found.")
                                    return self.render_to_response(self.get_context_data(form=form))

                                match_list.append(Matches.request_match(
                                    self.request.user, form.cleaned_data['bot1'],
                                    bot2, form.cleaned_data['map']))
                        else:  # specific_matchup
                            for _ in range(0, form.cleaned_data['match_count']):
                                match_list.append(Matches.request_match(
                                    self.request.user, form.cleaned_data['bot1'],
                                    form.cleaned_data['bot2'], form.cleaned_data['map']))

                    message = ""
                    for match in match_list:
                        message += f"<a href='{reverse('match', kwargs={'pk': match.id})}'>Match {match.id}</a> created.<br/>"
                    messages.success(self.request, mark_safe(message))
                    return super().form_valid(form)
                else:
                    messages.error(self.request, "That number of matches exceeds your match request limit.")
                    return self.render_to_response(self.get_context_data(form=form))
            else:
                messages.error(self.request, "Sorry - you cannot request matches between the same bot.")
                return self.render_to_response(self.get_context_data(form=form))
        else:
            messages.error(self.request, "Sorry. Requested matches are currently disabled.")
            return self.render_to_response(self.get_context_data(form=form))
