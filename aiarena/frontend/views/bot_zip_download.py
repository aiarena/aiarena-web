from private_storage.views import PrivateStorageDetailView

from aiarena.core.models import Bot


class BotZipDownloadView(PrivateStorageDetailView):
    model = Bot
    model_file_field = "bot_zip"

    content_disposition = "attachment"

    def get_content_disposition_filename(self, private_file):
        return f"{private_file.parent_object.name}.zip"

    def can_access_file(self, private_file):
        user = private_file.request.user
        # Allow if staff, the owner of the file, or the file is marked as publicly downloadable
        return (
            user.is_authenticated
            and user.is_staff
            or private_file.parent_object.user == user
            or private_file.parent_object.bot_zip_publicly_downloadable
        )
