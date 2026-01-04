from django.core.cache import cache
from django.db.models import Case, Count, IntegerField, Prefetch, Sum, Value, When
from django.views.generic import ListView

from constance import config

from aiarena.core.models import Bot, Competition, CompetitionParticipation, News, Round, User
from aiarena.core.services import ladders


class Index(ListView):
    def get_queryset(self):
        """This was applicable before multiple competitions and has only been left here to avoid having to refactor
        the code"""
        return CompetitionParticipation.objects.none()

    def get_competitions(self):
        competition_context = []
        cache_time = config.TOP10_CACHE_TIME
        competitions = (
            Competition.objects.only("name", "interest", "n_divisions", "n_placements")
            .filter(status__in=["frozen", "paused", "open", "closing"])
            .annotate(num_participants=Count("participations"))
        )
        # Count active bots of the user in each competition
        if self.request.user.is_authenticated:
            competitions = competitions.annotate(
                n_active_bots=Sum(
                    Case(
                        When(participations__bot__user=self.request.user, participations__active=True, then=1),
                        default=0,
                        output_field=IntegerField(),
                    )
                )
            )
        else:
            competitions = competitions.annotate(n_active_bots=Value(0, IntegerField()))
        # Order competitions as they are to be shown on home page
        competitions = competitions.order_by("-n_active_bots", "-interest", "-num_participants", "n_placements")

        for comp in competitions:
            if Round.objects.filter(competition=comp).count() > 0:
                cache_key = f"{comp.id}-top10-cache"
                top10 = cache.get(cache_key)
                if top10 is None:
                    top10 = (
                        ladders.get_competition_ranked_participants(comp, amount=10)
                        .prefetch_related(
                            Prefetch("bot", queryset=Bot.objects.all().only("user_id", "name")),
                            Prefetch("bot__user", queryset=User.objects.all().only("patreon_level")),
                        )
                        .calculate_trend(comp)
                    )
                    cache.set(cache_key, top10, cache_time)

                competition_context.append(
                    {
                        "competition": comp,
                        "top10": top10,
                    }
                )
        return competition_context

    def get_news(self):
        cache_time = config.NEWS_CACHE_TIME
        cache_key = "news"
        news = cache.get(cache_key)
        if news is None:
            news = News.objects.all().order_by("-created")
            cache.set(cache_key, news, cache_time)
        return news

    def get_events(self):
        events = (
            Bot.objects.select_related("user")
            .only("user", "name", "created", "bot_zip_updated")
            .order_by("-bot_zip_updated")[:15]
        )
        for event in events:
            # if these are within a second, then the bot was created, not updated
            event.is_created_event = (event.bot_zip_updated - event.created).seconds <= 1
        return events

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context["events"] = self.get_events
        context["news"] = self.get_news()
        context["competitions"] = self.get_competitions()

        return context

    template_name = "index.html"
