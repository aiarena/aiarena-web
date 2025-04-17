from wsgiref.util import FileWrapper

from django.http import Http404, HttpResponse

from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.filters import OrderingFilter, SearchFilter

from aiarena.api.view_filters import BotFilter
from aiarena.api.views.include import bot_search_fields
from aiarena.api.views.permissions import BotAccessPermission
from aiarena.api.views.serializers import BotSerializer, BotUpdateSerializer
from aiarena.core.models import Bot


class BotViewSet(viewsets.mixins.UpdateModelMixin, viewsets.ReadOnlyModelViewSet):
    """
    Bot data view
    """

    queryset = Bot.objects.all().select_related("user")
    serializer_class = BotSerializer
    serializer_class_patch = BotUpdateSerializer

    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_class = BotFilter
    search_fields = bot_search_fields
    ordering_fields = bot_search_fields
    http_method_names = ["get", "options", "head", "trace", "patch"]

    def get_permissions(self):
        return [permission() for permission in self.permission_classes + [BotAccessPermission]]

    def get_serializer_class(self):
        if self.request.method == "PATCH":
            return self.serializer_class_patch
        return self.serializer_class

    def perform_update(self, serializer):
        if "wiki_article_content" in serializer.validated_data:
            serializer.instance.update_bot_wiki_article(
                new_content=serializer.validated_data["wiki_article_content"],
                request=self.request,
            )
        serializer.save()

    @action(detail=True, methods=["GET"], name="Download a bot's zip file", url_path="zip")
    def download_zip(self, request, *args, **kwargs):
        """
        Download a bot's zip file.
        TODO: this is a defunct feature. Downloads should be via AWS S3. Ideally this should be cleaned up.
        """
        try:
            bot = Bot.objects.get(id=kwargs["pk"])
            if bot.can_download_bot_zip(request.user):
                response = HttpResponse(FileWrapper(bot.bot_zip), content_type="application/zip")
                response["Content-Disposition"] = f'inline; filename="{bot.name}.zip"'
                return response
            else:
                raise Http404()
        except Bot.DoesNotExist:
            raise Http404()

    @action(detail=True, methods=["GET"], name="Download a bot's data file", url_path="data")
    def download_data(self, request, *args, **kwargs):
        """
        Download a bot's data file.
        TODO: this is a defunct feature. Downloads should be via AWS S3. Ideally this should be cleaned up.
        """
        try:
            bot = Bot.objects.get(id=kwargs["pk"])
            if bot.can_download_bot_data(request.user):
                response = HttpResponse(FileWrapper(bot.bot_data), content_type="application/zip")
                response["Content-Disposition"] = f'inline; filename="{bot.name}_data.zip"'
                return response
            else:
                raise Http404()
        except Bot.DoesNotExist:
            raise Http404()
