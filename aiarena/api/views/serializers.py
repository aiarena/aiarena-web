from django.contrib.auth import authenticate
from django.core.exceptions import ValidationError as DjangoValidationError

from rest_framework import serializers
from rest_framework.reverse import reverse

from aiarena.api.views.include import (
    bot_include_fields,
    bot_race_include_fields,
    competition_bot_map_stats_include_fields,
    competition_bot_matchup_stats_include_fields,
    competition_include_fields,
    competition_participation_include_fields,
    discord_user_include_fields,
    game_include_fields,
    game_mode_include_fields,
    map_include_fields,
    map_pool_include_fields,
    match_include_fields,
    matchparticipation_include_fields,
    matchtag_include_fields,
    news_include_fields,
    patreon_unlinked_uid_include_fields,
    result_include_fields,
    round_include_fields,
    trophy_include_fields,
    user_include_fields,
)
from aiarena.core.models import (
    Bot,
    Competition,
    CompetitionBotMapStats,
    CompetitionBotMatchupStats,
    CompetitionParticipation,
    Game,
    GameMode,
    Map,
    MapPool,
    Match,
    MatchParticipation,
    MatchTag,
    News,
    Result,
    Round,
    Trophy,
    User,
)
from aiarena.core.models.bot_race import BotRace
from aiarena.core.services import bots
from aiarena.patreon.models import PatreonUnlinkedDiscordUID
from discord_bind.models import DiscordUser


# From: https://www.guguweb.com/2022/01/23/django-rest-framework-authentication-the-easy-way/
class LoginSerializer(serializers.Serializer):
    """
    This serializer defines two fields for authentication:
      * username
      * password.
    It will try to authenticate the user with when validated.
    """

    username = serializers.CharField(label="Username", write_only=True)
    password = serializers.CharField(
        label="Password",
        # This will be used when the DRF browsable API is enabled
        style={"input_type": "password"},
        trim_whitespace=False,
        write_only=True,
    )

    def validate(self, attrs):
        # Take username and password from request
        username = attrs.get("username")
        password = attrs.get("password")

        if username and password:
            # Try to authenticate the user using Django auth framework.
            user = authenticate(request=self.context.get("request"), username=username, password=password)
            if not user:
                # If we don't have a regular user, raise a ValidationError
                msg = "Access denied: wrong username or password."
                raise serializers.ValidationError(msg, code="authorization")
        else:
            msg = 'Both "username" and "password" are required.'
            raise serializers.ValidationError(msg, code="authorization")
        # We have a valid user, put it in the serializer's validated_data.
        # It will be used in the view.
        attrs["user"] = user
        return attrs


class RequestMatchSerializer(serializers.Serializer):
    bot1 = serializers.PrimaryKeyRelatedField(queryset=Bot.objects.all())
    bot2 = serializers.PrimaryKeyRelatedField(queryset=Bot.objects.all())
    map = serializers.PrimaryKeyRelatedField(queryset=Map.objects.all())


class TrophySerializer(serializers.ModelSerializer):
    trophy_icon_name = serializers.SerializerMethodField()

    def get_trophy_icon_name(self, obj):
        return obj.icon.name

    trophy_icon_image = serializers.SerializerMethodField()

    def get_trophy_icon_image(self, obj):
        return obj.icon.image.url

    class Meta:
        model = Trophy
        fields = trophy_include_fields + (
            "trophy_icon_name",
            "trophy_icon_image",
        )


class BotRaceSerializer(serializers.ModelSerializer):
    class Meta:
        model = BotRace
        fields = bot_race_include_fields


class BotSerializer(serializers.ModelSerializer):
    bot_zip = serializers.SerializerMethodField()
    bot_zip_md5hash = serializers.SerializerMethodField()
    bot_data = serializers.SerializerMethodField()
    bot_data_md5hash = serializers.SerializerMethodField()
    trophies = TrophySerializer(many=True)
    plays_race = BotRaceSerializer()

    def get_bot_zip(self, obj):
        # only display if the user can download the file
        if obj.bot_zip and obj.can_download_bot_zip(self.context["request"].user):
            # provide an API based download url instead of website.
            return reverse("api_bot-download-zip", kwargs={"pk": obj.id}, request=self.context["request"])
        else:
            return None

    def get_bot_zip_md5hash(self, obj):
        # only display if the user can download the file
        if obj.can_download_bot_zip(self.context["request"].user):
            return obj.bot_zip_md5hash
        else:
            return None

    def get_bot_data(self, obj):
        # only display if the user can download the file
        if obj.bot_data and obj.can_download_bot_data(self.context["request"].user):
            # provide an API based download url instead of website.
            return reverse("api_bot-download-data", kwargs={"pk": obj.id}, request=self.context["request"])
        else:
            return None

    def get_bot_data_md5hash(self, obj):
        # only display if the user can download the file
        if obj.can_download_bot_data(self.context["request"].user):
            return obj.bot_data_md5hash
        else:
            return None

    class Meta:
        model = Bot
        fields = bot_include_fields + ("trophies",)


class BotUpdateSerializer(serializers.ModelSerializer):
    wiki_article_content = serializers.CharField(write_only=True)
    bot_zip = serializers.FileField(write_only=True)
    bot_data = serializers.FileField(write_only=True)

    class Meta:
        model = Bot
        fields = [
            "bot_zip",
            "bot_zip_publicly_downloadable",
            "bot_data",
            "bot_data_publicly_downloadable",
            "bot_data_enabled",
            "wiki_article_content",
        ]

    def validate_bot_zip(self, value):
        try:
            self.instance.validate_bot_zip_file(value)
        except DjangoValidationError as e:
            raise serializers.ValidationError(e)
        return value

    def validate_bot_data(self, value):
        if bots.bot_data_is_frozen(self.instance):
            raise serializers.ValidationError("Cannot edit bot_data when it's frozen (probably in a match)")
        return value


class CompetitionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Competition
        fields = competition_include_fields


class CompetitionBotMatchupStatsSerializer(serializers.ModelSerializer):
    class Meta:
        model = CompetitionBotMatchupStats
        fields = competition_bot_matchup_stats_include_fields


class CompetitionBotMapStatsSerializer(serializers.ModelSerializer):
    class Meta:
        model = CompetitionBotMapStats
        fields = competition_bot_map_stats_include_fields


class CompetitionParticipationSerializer(serializers.ModelSerializer):
    class Meta:
        model = CompetitionParticipation
        fields = competition_participation_include_fields


class DiscordUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = DiscordUser
        fields = discord_user_include_fields


class GameSerializer(serializers.ModelSerializer):
    class Meta:
        model = Game
        fields = game_include_fields


class GameModeSerializer(serializers.ModelSerializer):
    class Meta:
        model = GameMode
        fields = game_mode_include_fields


class MapSerializer(serializers.ModelSerializer):
    class Meta:
        model = Map
        fields = map_include_fields


class MapPoolSerializer(serializers.ModelSerializer):
    class Meta:
        model = MapPool
        fields = map_pool_include_fields


class ResultSerializer(serializers.ModelSerializer):
    bot1_name = serializers.SerializerMethodField()
    bot2_name = serializers.SerializerMethodField()

    def get_bot1_name(self, obj):
        return obj.match.participant1.bot.name

    def get_bot2_name(self, obj):
        return obj.match.participant2.bot.name

    class Meta:
        model = Result
        fields = result_include_fields + ("bot1_name", "bot2_name")


class MatchTagSerializer(serializers.ModelSerializer):
    tag_name = serializers.SerializerMethodField()

    def get_tag_name(self, obj):
        return obj.tag.name

    class Meta:
        model = MatchTag
        fields = matchtag_include_fields + ("tag_name",)


class MatchSerializer(serializers.ModelSerializer):
    result = ResultSerializer()
    tags = MatchTagSerializer(many=True)

    class Meta:
        model = Match
        fields = match_include_fields + ("result", "tags")


class MatchParticipationSerializer(serializers.ModelSerializer):
    match_log = serializers.SerializerMethodField()

    def get_match_log(self, obj):
        # only display if the user can download the file
        if obj.match_log and obj.can_download_match_log(self.context["request"].user):
            # provide an API based download url instead of website.
            return reverse(
                "api_matchparticipation-download-match-log", kwargs={"pk": obj.id}, request=self.context["request"]
            )
        else:
            return None

    class Meta:
        model = MatchParticipation
        fields = matchparticipation_include_fields


class NewsSerializer(serializers.ModelSerializer):
    class Meta:
        model = News
        fields = news_include_fields


class PatreonUnlinkedDiscordUIDSerializer(serializers.ModelSerializer):
    class Meta:
        model = PatreonUnlinkedDiscordUID
        fields = patreon_unlinked_uid_include_fields


class RoundSerializer(serializers.ModelSerializer):
    class Meta:
        model = Round
        fields = round_include_fields


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = user_include_fields
