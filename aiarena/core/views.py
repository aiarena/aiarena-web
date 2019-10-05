from constance import config
from django import forms
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.db.models import F, Prefetch
from django.shortcuts import render
from django.urls import reverse
from django.views import View
from django.views.generic import CreateView, ListView, UpdateView, DetailView
from private_storage.views import PrivateStorageDetailView

from aiarena.core.models import Bot, Result, User, Round, Match, Participant


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
        context['max_active_per_race_bot_count'] = config.MAX_USER_BOT_COUNT_ACTIVE_PER_RACE
        return context


class UserProfileUpdateForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'discord_user', 'discord_tag']


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
    fields = ['name', 'bot_zip', 'plays_race', 'type']

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


class BotDetail(DetailView):
    model = Bot
    template_name = 'bot.html'

    def get_context_data(self, **kwargs):
        context = super(BotDetail, self).get_context_data(**kwargs)

        results = Result.objects.filter(match__participant__bot=self.object).order_by('-created')

        # paginate the results
        page = self.request.GET.get('page', 1)
        paginator = Paginator(results, 30)
        try:
            results = paginator.page(page)
        except PageNotAnInteger:
            results = paginator.page(1)
        except EmptyPage:
            results = paginator.page(paginator.num_pages)

        page_number = results.number

        # limit displayed page numbers
        if paginator.num_pages <= 11 or page_number <= 6:  # case 1 and 2
            results_page_range = [x for x in range(1, min(paginator.num_pages + 1, 12))]
        elif page_number > paginator.num_pages - 6:  # case 4
            results_page_range = [x for x in range(paginator.num_pages - 10, paginator.num_pages + 1)]
        else:  # case 3
            results_page_range = [x for x in range(page_number - 5, page_number + 6)]

        # retrieve the opponent and transform the result type to be personal to this bot
        for result in results:
            result.opponent = result.match.participant_set.exclude(bot=self.object).get()
            result.me = result.match.participant_set.get(bot=self.object)

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

        context['stats_bot_matchups'] = self.object.statsbotmatchups_set.all().order_by('opponent__name')
        context['result_list'] = results
        context['results_page_range'] = results_page_range
        return context


class StandardBotUpdateForm(forms.ModelForm):
    class Meta:
        model = Bot
        fields = ['active', 'active', 'bot_zip', 'bot_zip_publicly_downloadable', 'bot_data',
                  'bot_data_publicly_downloadable']


class FrozenDataBotUpdateForm(forms.ModelForm):
    bot_data = forms.FileField(disabled=True)

    class Meta:
        model = Bot
        fields = ['active', 'active', 'bot_zip', 'bot_zip_publicly_downloadable', 'bot_data',
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

    # change the available fields based upon whether the bot_data is available for editing or not.
    def get_form_class(self):
        if self.object.bot_data_is_currently_frozen():
            return FrozenDataBotUpdateForm
        else:
            return StandardBotUpdateForm


class AuthorList(ListView):
    queryset = User.objects.all().order_by('username').filter(is_active=1, service_account=False)
    template_name = 'authors.html'


class AuthorDetail(DetailView):
    model = User
    template_name = 'author.html'
    context_object_name = 'author'  # change the context name to avoid overriding the current user oontext object

    def get_context_data(self, **kwargs):
        context = super(AuthorDetail, self).get_context_data(**kwargs)
        context['bot_list'] = Bot.objects.filter(user_id=self.object.id).order_by('-created')
        return context


# Using a ListView, which has automated behaviour for displaying a list of models
class Ranking(ListView):
    # If we wanted all the bots, we could just set this and, because we're extending a ListView, it would
    # understand to get all the Bots, which could be referenced as "bot_list" in the template.
    # model = Bot

    # Instead, because we want to filter the bots, we define queryset,
    # which is also referenced as "bot_list" in the template.
    queryset = Bot.objects.filter(active=1).order_by('-elo')

    # If we didn't set this, the ListView would default to searching for a template at <module>/<modelname>_list.html
    # In this case, that would be "core/bot_list.html"
    template_name = 'ranking.html'


class Results(ListView):
    queryset = Result.objects.all().order_by('-created')[:100].prefetch_related(
        Prefetch('winner'),
        Prefetch('match__participant_set', Participant.objects.all().prefetch_related('bot'), to_attr='participants'))
    template_name = 'results.html'


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
    model = Participant
    model_file_field = 'match_log'

    content_disposition = 'attachment'

    def get_content_disposition_filename(self, private_file):
        return '{0}_{1}_log.zip'.format(private_file.parent_object.bot.name, private_file.parent_object.id)

    def can_access_file(self, private_file):
        user = private_file.request.user
        # Allow if staff or the owner of the file
        return user.is_authenticated and user.is_staff or private_file.parent_object.bot.user == user


class Index(ListView):
    queryset = Bot.objects.filter(active=1).order_by('-elo')[:10]  # top 10 bots
    template_name = 'index.html'


class MatchQueue(View):
    def get(self, request):
        # Matches without a round are requested ones
        requested_matches = Match.objects.filter(round__isnull=True, result__isnull=True).order_by(
            F('started').asc(nulls_last=True), F('id').asc()).prefetch_related(
                Prefetch('map'),
                Prefetch('participant_set', Participant.objects.all().prefetch_related('bot'), to_attr='participants'))

        # Matches with a round
        rounds = Round.objects.filter(complete=False).order_by(F('id').asc())
        for round in rounds:
            round.matches = Match.objects.filter(round_id=round.id, result__isnull=True).order_by(
                F('started').asc(nulls_last=True), F('id').asc()).prefetch_related(
                Prefetch('map'),
                Prefetch('participant_set', Participant.objects.all().prefetch_related('bot'), to_attr='participants'))

        context = {'round_list': rounds, 'requested_matches': requested_matches}
        return render(request, 'match_queue.html', context)


class MatchDetail(DetailView):
    model = Match
    template_name = 'match.html'
