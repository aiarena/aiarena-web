from private_storage.views import PrivateStorageDetailView

from aiarena.core.models import CompetitionParticipation


class BotCompetitionStatsEloGraphUpdatePlot(PrivateStorageDetailView):
    model = CompetitionParticipation
    model_file_field = "elo_graph_update_plot"

    content_disposition = "inline"

    def get_content_disposition_filename(self, private_file):
        return "elo_graph_update_plot.png"

    def can_access_file(self, private_file):
        # Allow if the owner of the bot and a patreon supporter
        return (
            private_file.parent_object.bot.user == private_file.request.user
            and private_file.request.user.patreon_level != "None"
        )
