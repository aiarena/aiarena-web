from django import forms
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.shortcuts import render
from django.urls import reverse
from django.views import View
from django.views.generic import CreateView, ListView, UpdateView, DetailView
from private_storage.views import PrivateStorageDetailView

from aiarena.core.models import Bot, Result, User


class UserProfileForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['first_name', 'last_name']


class UserProfile(SuccessMessageMixin, LoginRequiredMixin, UpdateView):
    form_class = UserProfileForm
    redirect_field_name = 'next'
    template_name = 'profile.html'
    success_message = "Profile saved successfully"

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
        return context


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
    queryset = Bot.objects.filter(active=1).order_by('name')
    template_name = 'bots.html'


class BotDetail(DetailView):
    model = Bot
    template_name = 'bot.html'

    def get_context_data(self, **kwargs):
        context = super(BotDetail, self).get_context_data(**kwargs)

        results = Result.objects.filter(match__participant__bot=self.object).order_by('-created')[:10]

        # retrieve the opponent
        for result in results:
            result.opponent = result.match.participant_set.exclude(bot=self.object)[0]

        context['result_list'] = results
        return context


class StandardBotUpdateForm(forms.ModelForm):
    class Meta:
        model = Bot
        fields = ['active', 'active', 'bot_zip', 'bot_data']


class FrozenDataBotUpdateForm(forms.ModelForm):
    bot_data = forms.FileField(disabled=True)

    class Meta:
        model = Bot
        fields = ['active', 'active', 'bot_zip', 'bot_data']


# todo: don't allow editing a bot when in a match
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


# Using a View - pretty bare-bones
class Results(View):
    def get(self, request):
        results = Result.objects.all().order_by('-created')[:100]
        for result in results:
            result.bot1 = result.match.participant_set.filter(participant_number=1)[0]
            result.bot2 = result.match.participant_set.filter(participant_number=2)[0]
        context = {'result_list': results}
        return render(request, 'results.html', context)


class BotZipDownloadView(PrivateStorageDetailView):
    model = Bot
    model_file_field = 'bot_zip'

    content_disposition = 'attachment'

    def get_content_disposition_filename(self, private_file):
        return '{0}.zip'.format(private_file.parent_object.name)

    def can_access_file(self, private_file):
        user = private_file.request.user
        # Only allow staff or the owner of the file
        # temp hack to get arena clients working again.
        return True  # user.is_authenticated and user.is_staff or private_file.parent_object.user == user


class BotDataDownloadView(PrivateStorageDetailView):
    model = Bot
    model_file_field = 'bot_data'

    content_disposition = 'attachment'

    def get_content_disposition_filename(self, private_file):
        return '{0}_data.zip'.format(private_file.parent_object.name)

    def can_access_file(self, private_file):
        user = private_file.request.user
        # Only allow staff or the owner of the file
        # temp hack to get arena clients working again.
        return True  # user.is_authenticated and user.is_staff or private_file.parent_object.user == user
