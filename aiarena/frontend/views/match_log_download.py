from private_storage.views import PrivateStorageDetailView

from aiarena.core.models import MatchParticipation


class MatchLogDownloadView(PrivateStorageDetailView):
    model = MatchParticipation
    model_file_field = "match_log"

    content_disposition = "attachment"

    def get_content_disposition_filename(self, private_file):
        return f"{private_file.parent_object.bot.name}_{private_file.parent_object.id}_log.zip"

    def can_access_file(self, private_file):
        user = private_file.request.user
        # Allow if staff or the owner of the file
        return user.is_authenticated and user.is_staff or private_file.parent_object.bot.user == user
