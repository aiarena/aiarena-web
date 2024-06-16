from django.views.generic import DetailView

from aiarena.core.models import Round


class RoundDetail(DetailView):
    model = Round
    template_name = "round.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        matches_finished = 0
        matches_started = 0
        matches_queued = 0

        matches = self.object.match_set.all()
        for match in matches:
            if match.status == "Finished":
                matches_finished += 1
            elif match.status == "Started":
                matches_started += 1
            elif match.status == "Queued":
                matches_queued += 1
            else:
                raise "A match had an unknown status!"

        context["matches_finished"] = matches_finished
        context["matches_started"] = matches_started
        context["matches_queued"] = matches_queued

        return context
