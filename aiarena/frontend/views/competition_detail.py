from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator
from django.db.models import Prefetch
from django.views.generic import DetailView

from aiarena.core.models import Bot, Competition, CompetitionParticipation, Round, User
from aiarena.core.services import ladders
from aiarena.frontend.utils import restrict_page_range


class CompetitionDetail(DetailView):
    model = Competition
    template_name = "competition.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context["maps"] = self.object.maps.all()

        rounds = Round.objects.filter(competition_id=self.object.id).order_by("-id")
        page = self.request.GET.get("page", 1)
        paginator = Paginator(rounds, 30)
        try:
            rounds = paginator.page(page)
        except PageNotAnInteger:
            rounds = paginator.page(1)
        except EmptyPage:
            rounds = paginator.page(paginator.num_pages)
        context["round_list"] = rounds
        context["round_page_range"] = restrict_page_range(paginator.num_pages, rounds.number)

        all_participants = ladders.get_competition_display_full_rankings(self.object)
        all_participants = all_participants.prefetch_related(
            Prefetch(
                "bot",
                queryset=Bot.objects.all()
                .select_related("plays_race")
                .only("plays_race", "user_id", "name", "type", "plays_race"),
            ),
            Prefetch("bot__user", queryset=User.objects.all().only("patreon_level", "username", "type")),
        ).calculate_trend(self.object)

        context["divisions"] = dict()
        to_title = lambda x: "Awaiting Entry" if x == CompetitionParticipation.DEFAULT_DIVISION else f"Division {x}"
        for participant in all_participants:
            if to_title(participant.division_num) not in context["divisions"]:
                context["divisions"][to_title(participant.division_num)] = []
            context["divisions"][to_title(participant.division_num)].append(participant)
        return context
