from django.views.generic import ListView

from aiarena.core.models import Bot
from aiarena.frontend.utils import restrict_page_range


class BotList(ListView):
    queryset = (
        Bot.objects.all()
        .only("name", "plays_race", "type", "user__username", "user__type")
        .select_related("user", "plays_race")
        .order_by("name")
    )
    template_name = "bots.html"
    paginate_by = 50

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # add the page ranges
        page_obj = context["page_obj"]
        context["page_range"] = restrict_page_range(page_obj.paginator.num_pages, page_obj.number)

        return context


class BotDownloadableList(ListView):
    queryset = (
        Bot.objects.filter(bot_zip_publicly_downloadable=True)
        .only("name", "plays_race", "type", "user__username", "user__type")
        .select_related("user")
        .order_by("name")
    )
    template_name = "bots_downloadable.html"
    paginate_by = 50

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # add the page ranges
        page_obj = context["page_obj"]
        context["page_range"] = restrict_page_range(page_obj.paginator.num_pages, page_obj.number)

        return context
