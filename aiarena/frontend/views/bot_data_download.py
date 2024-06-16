from private_storage.views import PrivateStorageDetailView

from aiarena.core.models import Bot


class BotDataDownloadView(PrivateStorageDetailView):
    model = Bot
    model_file_field = "bot_data"

    content_disposition = "attachment"

    def get_content_disposition_filename(self, private_file):
        return f"{private_file.parent_object.name}_data.zip"

    def can_access_file(self, private_file):
        user = private_file.request.user
        # Allow if staff, the owner of the file, or the file is marked as publicly downloadable
        return (
            user.is_authenticated
            and user.is_staff
            or private_file.parent_object.user == user
            or private_file.parent_object.bot_data_publicly_downloadable
        )
