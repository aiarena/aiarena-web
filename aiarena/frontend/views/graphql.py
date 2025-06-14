from django.conf import settings

from graphene_file_upload.django import FileUploadGraphQLView
from graphql import GraphQLError

from aiarena.core.exceptions import AIArenaException


class CustomGraphQLView(FileUploadGraphQLView):
    mask_exceptions = not settings.DEBUG
    masked_error_message = "Something went wrong. Please try again later."

    whitelisted_errors = [
        AIArenaException,
        GraphQLError,
    ]

    def format_error(self, error):
        formatted_error = super().format_error(error)
        if not self.mask_exceptions:
            return formatted_error

        original_error = getattr(error, "original_error", error)
        if any(isinstance(original_error, whitelisted_error) for whitelisted_error in self.whitelisted_errors):
            return formatted_error

        formatted_error["message"] = self.masked_error_message
        return formatted_error
