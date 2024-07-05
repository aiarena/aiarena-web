import logging

from django.conf import settings

from constance import config
from rest_framework import serializers, viewsets
from rest_framework.pagination import CursorPagination

from aiarena.core.models import CompetitionParticipation, Match, Result
from aiarena.core.permissions import IsServiceOrAdminUser


logger = logging.getLogger(__name__)


# Front facing serializer used by the view. Combines the other serializers together.
class StreamNextReplaySerializer(serializers.ModelSerializer):
    bot1_name = serializers.SerializerMethodField()
    bot2_name = serializers.SerializerMethodField()

    def get_bot1_name(self, obj: Result):
        return self.__get_participant_name(obj, 1)

    def get_bot2_name(self, obj: Result):
        return self.__get_participant_name(obj, 2)

    def __get_participant_name(self, obj, participant_number):
        # Manually filtering via a for loop is faster than using the ORM
        # in this case because matchparticipation_set is already prefetched
        for mp in obj.match.matchparticipation_set.all():
            if mp.participant_number == participant_number:
                return mp.bot.name
        raise Exception(f"Could not find bot name for participant number {participant_number} in match {obj.match.id}")

    class Meta:
        model = Result
        fields = (
            "match",
            "type",
            "replay_file",
            "bot1_name",
            "bot2_name",
        )
        read_only_fields = (
            "match",
            "type",
            "replay_file",
            "bot1_name",
            "bot2_name",
        )


class StreamNextReplayViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Filtered replays for streaming.
    """

    serializer_class = StreamNextReplaySerializer
    permission_classes = [IsServiceOrAdminUser]
    pagination_class = CursorPagination
    swagger_schema = None  # exclude this from swagger generation

    def get_queryset(self):
        # Filter competition participations above the starting ELO and exclude house bots
        competition_participations = CompetitionParticipation.objects.filter(elo__gte=settings.ELO_START_VALUE).exclude(
            bot__user_id=config.HOUSE_BOTS_USER_ID
        )

        # Filter matches that featured a bot from the filtered competition participations
        matches = Match.objects.filter(
            result__isnull=False,
            requested_by__isnull=True,
            matchparticipation__bot__competition_participations__in=competition_participations,
        )

        # Filter results that are either wins or surrenders and order them by the created date in descending order
        results = (
            Result.objects.filter(
                type__in=["Player1Win", "Player2Win", "Player1Surrender", "Player2Surrender"],
                match__in=matches,
            )
            .prefetch_related("match__matchparticipation_set__bot")
            .order_by("-created")
            .only("match", "type", "replay_file")
        )

        return results
