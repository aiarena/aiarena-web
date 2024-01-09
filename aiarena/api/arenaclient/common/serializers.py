from rest_framework import serializers
from rest_framework.fields import FileField, FloatField
from rest_framework.reverse import reverse

from aiarena.core.models import ArenaClientStatus, Bot, Map, Match, MatchParticipation, Result
from aiarena.core.s3_helpers import get_file_s3_url_with_content_disposition, is_s3_file
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
        # This is_s3_file check is a quick fix to avoid having to figure out how to restructure the storage backend.
        # The parameters in get_file_s3_url_with_content_disposition can only be specified with the S3 backend, else
        # it breaks.
        if is_s3_file(obj.bot_zip):
            return get_file_s3_url_with_content_disposition(obj.bot_zip, f"{obj.name}.zip")
        else:
            p = MatchParticipation.objects.only("participant_number").get(bot=obj, match_id=self.root.instance.id)
            return reverse(
                "match-download-zip",
                kwargs={"pk": self.root.instance.id, "p_num": p.participant_number},
                request=self.context["request"],
            )

    def get_bot_data(self, obj):
        p = (
            MatchParticipation.objects.select_related("bot")
            .only("use_bot_data", "bot__bot_data", "participant_number")
            .get(bot=obj, match_id=self.root.instance.id)
        )
        if p.use_bot_data and p.bot.bot_data:
            # This is_s3_file check is a quick fix to avoid having to figure out how to restructure the storage backend.
            # The parameters in get_file_s3_url_with_content_disposition can only be specified with the S3 backend, else
            # it breaks.
            if is_s3_file(obj.bot_data):
                return get_file_s3_url_with_content_disposition(obj.bot_data, f"{obj.name}_data.zip")
            else:
                return reverse(
                    "match-download-data",
                    kwargs={"pk": self.root.instance.id, "p_num": p.participant_number},
                    request=self.context["request"],
                )
        else:
            return None

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
