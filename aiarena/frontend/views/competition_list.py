from django.views.generic import ListView

from aiarena.core.models import Competition


class CompetitionList(ListView):
    queryset = Competition.objects.exclude(status="closed").order_by("-id")
    template_name = "competitions.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["closed_competitions"] = Competition.objects.filter(status="closed").order_by("-id")

        return context
