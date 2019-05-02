from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.shortcuts import render
from django.urls import reverse
from django.views import View
from django.views.generic import CreateView, ListView, DetailView

from aiarena.core.models import Bot, Result


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

        results = Result.objects.filter(match__participant__bot=self.object).order_by('-created')[:10]

        # retrieve the opponent
        for result in results:
            result.opponent = result.match.participant_set.exclude(bot=self.object)[0]

        context['result_list'] = results
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

    # Old code for reference.
    # def get(self, request):
    #     bot_ranking = Bot.objects.filter(active=1).order_by('-elo')
    #     context = {'bot_ranking': bot_ranking}
    #     return render(request, 'ranking.html', context)


# Using a View - pretty bare-bones
class Results(View):
    def get(self, request):
        results = Result.objects.all().order_by('-created')[:100]
        for result in results:
            result.bot1 = result.match.participant_set.filter(participant_number=1)[0]
            result.bot2 = result.match.participant_set.filter(participant_number=2)[0]
        context = {'result_list': results}
        return render(request, 'results.html', context)
