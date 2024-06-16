from django import forms
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.db.models import Q
from django.http import Http404
from django.urls import reverse
from django.views.generic import CreateView

from aiarena.core.models import Bot, Competition, CompetitionParticipation


class CompetitionParticipationForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        bot_id = kwargs.pop("bot_id")
        super().__init__(*args, **kwargs)
        self.fields["competition"].queryset = Competition.objects.exclude(
            Q(status__in=["closing", "closed"]) | Q(participations__bot_id=bot_id)
        )

    class Meta:
        model = CompetitionParticipation
        fields = [
            "competition",
        ]


class CompetitionParticipationList(SuccessMessageMixin, LoginRequiredMixin, CreateView):
    template_name = "bot_competitions.html"
    form_class = CompetitionParticipationForm

    redirect_field_name = "next"
    success_message = "Competition joined."

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["competitionparticipation_list"] = CompetitionParticipation.objects.filter(bot_id=self.kwargs["pk"])

        try:
            context["bot"] = Bot.objects.get(id=self.kwargs["pk"], user=self.request.user)
        except Bot.DoesNotExist:
            # avoid users accessing another user's bot
            raise Http404("No bot found matching the query")

        return context

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs.update({"bot_id": self.kwargs["pk"]})

        # set the associated bot
        if kwargs["instance"] is None:
            kwargs["instance"] = CompetitionParticipation()
        kwargs["instance"].bot = Bot.objects.get(pk=self.kwargs["pk"])
        return kwargs

    def get_login_url(self):
        return reverse("login")

    def get_success_url(self):
        return reverse("bot_competitions", kwargs={"pk": self.object.bot_id})
