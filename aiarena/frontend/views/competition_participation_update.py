from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.urls import reverse
from django.views.generic import UpdateView

from aiarena.core.models import CompetitionParticipation


class CompetitionParticipationUpdate(SuccessMessageMixin, LoginRequiredMixin, UpdateView):
    template_name = "bot_competitionparticipation_edit.html"
    model = CompetitionParticipation
    fields = [
        "active",
    ]

    redirect_field_name = "next"
    success_message = "Competition participation updated."

    def form_valid(self, form):
        self.object = form.save()
        if not self.object.active:
            self.object.division_num = CompetitionParticipation.DEFAULT_DIVISION
        return super(UpdateView, self).form_valid(form)

    def get_login_url(self):
        return reverse("login")

    def get_success_url(self):
        return reverse("bot_competitions", kwargs={"pk": self.kwargs["bot_id"]})

    def get_queryset(self):
        queryset = super().get_queryset()
        return queryset.filter(bot__user=self.request.user)
