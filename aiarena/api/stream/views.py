import logging

from constance import config
from rest_framework import viewsets, serializers

from aiarena.core.models import Result, Bot, Match, CompetitionParticipation, User
from aiarena.core.permissions import IsServiceOrAdminUser
from aiarena.settings import ELO_START_VALUE

logger = logging.getLogger(__name__)


# Front facing serializer used by the view. Combines the other serializers together.
class StreamNextReplaySerializer(serializers.ModelSerializer):
    bot1_name = serializers.SerializerMethodField()
    bot2_name = serializers.SerializerMethodField()

    def get_bot1_name(self, obj):
        return Bot.objects.get(matchparticipation__match=obj.match, matchparticipation__participant_number=1).name

    def get_bot2_name(self, obj):
        return Bot.objects.get(matchparticipation__match=obj.match, matchparticipation__participant_number=2).name

    class Meta:
        model = Result
        fields = 'match', 'type', 'replay_file', 'bot1_name', 'bot2_name',
        read_only_fields = 'match', 'type', 'replay_file', 'bot1_name', 'bot2_name',


class StreamNextReplayViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Filtered replays for streaming.
    """
    serializer_class = StreamNextReplaySerializer
    permission_classes = [IsServiceOrAdminUser]
    swagger_schema = None  # exclude this from swagger generation

    def get_queryset(self):
        # Only matches that featured a bot above the starting ELO
        # exclude matches with only house bots.
        matches = Match.objects.filter(result__isnull=False, requested_by__isnull=True,
                                       matchparticipation__bot__competition_participations__in=
                                       CompetitionParticipation.objects.filter(elo__gte=ELO_START_VALUE)
                                       .exclude(bot__user_id=config.HOUSE_BOTS_USER_ID))

        return Result.objects.filter(
            type__in=['Player1Win', 'Player2Win', 'Player1Surrender', 'Player2Surrender', ],  # Only wins/surrenders
            match__in=matches
        ).order_by('-created')

