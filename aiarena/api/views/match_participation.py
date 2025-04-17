from wsgiref.util import FileWrapper

from django.http import Http404, HttpResponse

from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.filters import OrderingFilter, SearchFilter

from aiarena.api.view_filters import MatchParticipationFilter
from aiarena.api.views.include import matchparticipation_filter_fields
from aiarena.api.views.serializers import MatchParticipationSerializer
from aiarena.core.models import MatchParticipation


class MatchParticipationViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Result data view
    """

    queryset = MatchParticipation.objects.all().select_related("bot", "bot__user")
    serializer_class = MatchParticipationSerializer

    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_class = MatchParticipationFilter
    search_fields = matchparticipation_filter_fields
    ordering_fields = matchparticipation_filter_fields

    @action(detail=True, methods=["GET"], name="Download a bot's zip file", url_path="match-log")
    def download_match_log(self, request, *args, **kwargs):
        mp = MatchParticipation.objects.get(id=kwargs["pk"])
        if mp.can_download_match_log(request.user):
            response = HttpResponse(FileWrapper(mp.match_log), content_type="application/zip")
            response["Content-Disposition"] = f'inline; filename="{mp.match_id}_{mp.bot.name}.zip"'
            return response
        else:
            raise Http404()
