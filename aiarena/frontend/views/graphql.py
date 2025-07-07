from django.conf import settings
from django.core.exceptions import ValidationError

import sentry_sdk
from graphene_file_upload.django import FileUploadGraphQLView
from graphql import GraphQLError

from aiarena.core.exceptions import AIArenaException
from aiarena.graphql.common import AccessDenied


class CustomGraphQLView(FileUploadGraphQLView):
    masked_error_message = "Something went wrong. Please try again later."

    whitelisted_errors = [
        AIArenaException,
        ValidationError,
        GraphQLError,
    ]

    def execute_graphql_request(self, *args, **kwargs):
        result = super().execute_graphql_request(*args, **kwargs)
        if result and result.errors:
            self._capture_sentry_exceptions(result.errors)
        return result

    def _capture_sentry_exceptions(self, errors):
        for error in errors:
            exc = getattr(error, "original_error", error)
            if isinstance(exc, AccessDenied):
                continue
            if settings.DEBUG:
                raise exc
            sentry_sdk.capture_exception(exc)

    def format_error(self, error):
        formatted_error = super().format_error(error)

        original_error = getattr(error, "original_error", error)
        if any(isinstance(original_error, whitelisted_error) for whitelisted_error in self.whitelisted_errors):
            return formatted_error

        formatted_error["message"] = self.masked_error_message
        return formatted_error
