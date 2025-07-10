from rest_framework import serializers
from rest_framework.fields import FileField, FloatField

from aiarena.api.arenaclient.common.file_utils import get_bot_data_url, get_bot_zip_url
from aiarena.core.models import ArenaClientStatus, Bot, Map, Match, MatchParticipation, Result
from aiarena.core.validators import validate_not_inf, validate_not_nan


class MapSerializer(serializers.ModelSerializer):
    class Meta:
        model = Map
        fields = "__all__"


class BotSerializer(serializers.ModelSerializer):
    # Dynamically regenerate bot_zip and bot_data urls to point to the API endpoints
    # Otherwise they will point to the front-end download views, which the API client won't
    # be authenticated for.
    bot_zip = serializers.SerializerMethodField()
    bot_data = serializers.SerializerMethodField()
    plays_race = serializers.CharField(source="plays_race.label")

    def get_bot_zip(self, obj):
        return get_bot_zip_url(obj, self.root.instance.id, context=self.context)

    def get_bot_data(self, obj):
        return get_bot_data_url(obj, self.root.instance.id, context=self.context)

    class Meta:
        model = Bot
        fields = (
            "id",
            "name",
            "game_display_id",
            "bot_zip",
            "bot_zip_md5hash",
            "bot_data",
            "bot_data_md5hash",
            "plays_race",
            "type",
        )


class MatchSerializer(serializers.ModelSerializer):
    bot1 = BotSerializer(read_only=True)
    bot2 = BotSerializer(read_only=True)
    map = MapSerializer(read_only=True)

    class Meta:
        model = Match
        fields = ("id", "bot1", "bot2", "map")


class SubmitResultResultSerializer(serializers.ModelSerializer):
    def validate(self, attrs):
        instance = SubmitResultResultSerializer.Meta.model(**attrs)
        instance.clean()  # enforce model validation
        return attrs

    class Meta:
        model = Result
        fields = "match", "type", "replay_file", "game_steps", "submitted_by", "arenaclient_log"


class SubmitResultBotSerializer(serializers.ModelSerializer):
    class Meta:
        model = Bot
        fields = ("bot_data",)


class SubmitResultParticipationSerializer(serializers.ModelSerializer):
    class Meta:
        model = MatchParticipation
        fields = "avg_step_time", "match_log", "result", "result_cause"


# Front facing serializer used by the view. Combines the other serializers together.
class SubmitResultCombinedSerializer(serializers.Serializer):
    # Result
    match = serializers.IntegerField()
    type = serializers.ChoiceField(choices=Result.TYPES)
    replay_file = serializers.FileField(required=False)
    game_steps = serializers.IntegerField()
    submitted_by = serializers.HiddenField(default=serializers.CurrentUserDefault())
    arenaclient_log = FileField(required=False)
    # Bot
    bot1_data = FileField(required=False)
    bot2_data = FileField(required=False)
    # Participant
    bot1_log = FileField(required=False)
    bot2_log = FileField(required=False)
    bot1_avg_step_time = FloatField(required=False, validators=[validate_not_nan, validate_not_inf])
    bot2_avg_step_time = FloatField(required=False, validators=[validate_not_nan, validate_not_inf])

    # tags
    bot1_tags = serializers.ListField(required=False, child=serializers.CharField(allow_blank=True))
    bot2_tags = serializers.ListField(required=False, child=serializers.CharField(allow_blank=True))


class SetArenaClientStatusSerializer(serializers.ModelSerializer):
    class Meta:
        model = ArenaClientStatus
        fields = ("status",)
