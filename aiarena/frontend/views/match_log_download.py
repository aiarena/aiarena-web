from private_storage.views import PrivateStorageDetailView

from aiarena.core.models import MatchParticipation
from aiarena.core.services.download_rate_limiting import check_download_rate_limit


class MatchLogDownloadView(PrivateStorageDetailView):
    model = MatchParticipation
    model_file_field = "match_log"

    content_disposition = "attachment"

    def get_content_disposition_filename(self, private_file):
        return f"{private_file.parent_object.bot.name}_{private_file.parent_object.id}_log.zip"

    def can_access_file(self, private_file):
        user = private_file.request.user
        # Allow if staff or the owner of the file
        allowed = user.is_authenticated and user.is_staff or private_file.parent_object.bot.user == user
        if allowed:
            # Legacy app-proxied download: metered here at serve time rather than at
            # S3-link issuance. Should migrate to a presigned S3 URL via GraphQL.
            check_download_rate_limit(user, private_file.parent_object.match_log)
        return allowed
