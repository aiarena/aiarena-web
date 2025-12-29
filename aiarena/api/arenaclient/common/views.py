import logging
from wsgiref.util import FileWrapper

from django.core.cache import cache
from django.http import HttpResponse

from constance import config
from rest_framework import mixins, status, viewsets
from rest_framework.decorators import action
from rest_framework.exceptions import PermissionDenied
from rest_framework.response import Response

from aiarena.core.models import (
    Match,
    MatchParticipation,
)
from aiarena.core.permissions import IsArenaClient, IsArenaClientOrAdminUser

from .ac_coordinator import ACCoordinator
from .exceptions import LadderDisabled, NoGameForClient
from .result_submission_handler import handle_result_submission
from .serializers import (
    MatchSerializer,
    SetArenaClientStatusSerializer,
    SubmitResultCombinedSerializer,
)


logger = logging.getLogger(__name__)


class MatchViewSet(viewsets.GenericViewSet):
    """
    MatchViewSet implements a POST method with no field requirements, which will create a match and return the JSON.
    No reading of models is implemented.
    """

    serializer_class = MatchSerializer
    permission_classes = [IsArenaClientOrAdminUser]
    throttle_scope = "arenaclient"
    swagger_schema = None  # exclude this from swagger generation

    def load_participants(self, match: Match):
        match.bot1 = (
            MatchParticipation.objects.select_related("bot")
            .only("bot")
            .get(match_id=match.id, participant_number=1)
            .bot
        )
        match.bot2 = (
            MatchParticipation.objects.select_related("bot")
            .only("bot")
            .get(match_id=match.id, participant_number=2)
            .bot
        )

    def create(self, request, *args, **kwargs):
        no_game_available = cache.get("NoGameAvailable", False)

        if request.user.is_arenaclient:
            match = ACCoordinator.next_match(request.user.arenaclient, no_game_available)
            if match:
                self.load_participants(match)

                serializer = self.get_serializer(match)
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            else:
                if not no_game_available:
                    cache.set("NoGameAvailable", True, config.GAME_AVAILABLE_CACHE_TIME)

        raise NoGameForClient()

    # todo: check match is in progress/bot is in this match
    @action(
        detail=True,
        methods=["GET"],
        name="Download a participant's zip file",
        url_path=r"(?P<p_num>\d+)/zip",
    )
    def download_zip(self, request, *args, **kwargs):
        p = MatchParticipation.objects.get(match=kwargs["pk"], participant_number=kwargs["p_num"])
        if p.bot.can_download_bot_zip(request.user):
            response = HttpResponse(FileWrapper(p.bot.bot_zip), content_type="application/zip")
            response["Content-Disposition"] = f'inline; filename="{p.bot.name}.zip"'
            return response
        else:
            raise PermissionDenied("You cannot download that bot zip.")

    # todo: check match is in progress/bot is in this match
    @action(
        detail=True,
        methods=["GET"],
        name="Download a participant's data file",
        url_path=r"(?P<p_num>\d+)/data",
    )
    def download_data(self, request, *args, **kwargs):
        p = MatchParticipation.objects.get(match=kwargs["pk"], participant_number=kwargs["p_num"])
        if p.bot.can_download_bot_data(request.user):
            response = HttpResponse(FileWrapper(p.bot.bot_data), content_type="application/zip")
            response["Content-Disposition"] = f'inline; filename="{p.bot.name}_data.zip"'
            return response
        else:
            raise PermissionDenied("You cannot download that bot data.")


class ResultViewSet(mixins.CreateModelMixin, viewsets.GenericViewSet):
    """
    ResultViewSet implements a POST method to log a result.
    No reading of models is implemented.
    """

    serializer_class = SubmitResultCombinedSerializer
    permission_classes = [IsArenaClientOrAdminUser]
    # Don't throttle result submissions - we can never have "too many" result submissions.
    # throttle_scope = 'arenaclient'
    swagger_schema = None  # exclude this from swagger generation

    def create(self, request, *args, **kwargs):
        if not config.LADDER_ENABLED:
            raise LadderDisabled()

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        match_id = serializer.validated_data["match"]

        logger.debug(
            f"Result submission. "
            f"match: {serializer.validated_data.get('match')} "
            f"type: {serializer.validated_data.get('type')} "
            f"replay_file: {serializer.validated_data.get('replay_file')} "
            f"game_steps: {serializer.validated_data.get('game_steps')} "
            f"submitted_by: {serializer.validated_data.get('submitted_by')} "
            f"arenaclient_log: {serializer.validated_data.get('arenaclient_log')} "
            f"bot1_avg_step_time: {serializer.validated_data.get('bot1_avg_step_time')} "
            f"bot1_log: {serializer.validated_data.get('bot1_log')} "
            f"bot1_data: {serializer.validated_data.get('bot1_data')} "
            f"bot1_tags: {serializer.validated_data.get('bot1_tags')} "
            f"bot2_avg_step_time: {serializer.validated_data.get('bot2_avg_step_time')} "
            f"bot2_log: {serializer.validated_data.get('bot2_log')} "
            f"bot2_data: {serializer.validated_data.get('bot2_data')} "
            f"bot2_tags: {serializer.validated_data.get('bot2_tags')} "
        )

        result = handle_result_submission(match_id, serializer.validated_data)

        headers = self.get_success_headers(serializer.data)
        return Response({"result_id": result.id}, status=status.HTTP_201_CREATED, headers=headers)


class SetArenaClientStatusViewSet(mixins.CreateModelMixin, viewsets.GenericViewSet):
    """
    SetArenaClientStatusViewSet implements a POST method to record an arena client's status.
    No reading of models is implemented.
    """

    serializer_class = SetArenaClientStatusSerializer
    permission_classes = [IsArenaClient]
    swagger_schema = None  # exclude this from swagger generation

    def perform_create(self, serializer):
        serializer.save(arenaclient=self.request.user.arenaclient)
