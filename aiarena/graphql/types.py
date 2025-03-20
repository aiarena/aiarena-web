import graphene
from avatar.models import Avatar
from django_filters import FilterSet, OrderingFilter
from graphene_django import DjangoConnectionField
from graphene_django.filter import DjangoFilterConnectionField
from rest_framework.authtoken.models import Token

from aiarena.core import models
from aiarena.core.services import Ladders, MatchRequests, SupporterBenefits
from aiarena.graphql.common import CountingConnection, DjangoObjectTypeWithUID


class UserType(DjangoObjectTypeWithUID):
    # This is the public user type.
    # put data everyone should be able view here.

    own_bots = DjangoFilterConnectionField("aiarena.graphql.BotType")
    avatar_url = graphene.String()

    class Meta:
        model = models.User
        fields = [
            "id",
            "username",
            "patreon_level",
            "date_joined",
        ]
        filter_fields = []

    @staticmethod
    def resolve_own_bots(root: models.User, info, **args):
        return root.bots.all()

    @staticmethod
    def resolve_avatar_url(root: models.User, info):
        avatar_instance = Avatar.objects.filter(user=root).order_by("-primary", "-date_uploaded").first()

        if avatar_instance:
            avatar_url = avatar_instance.get_absolute_url()
            return info.context.build_absolute_uri(avatar_url)
            # We can also return "avatar_url" if we want a relative url
            # return  avatar_url
        return None  # Return None if no avatar exists. However, we probably want to return the default avatar.


class BotFilterSet(FilterSet):
    order_by = OrderingFilter(
        fields=[
            "bot_zip_updated",
        ]
    )
    user_id = graphene.ID()

    class Meta:
        model = models.Bot
        fields = ["name", "user_id", "order_by"]


class BotType(DjangoObjectTypeWithUID):
    url = graphene.String()
    competition_participations = DjangoFilterConnectionField("aiarena.graphql.CompetitionParticipationType")
    wiki_article = graphene.String()
    match_participations = DjangoFilterConnectionField("aiarena.graphql.MatchParticipationType")
    plays_race = graphene.String()

    class Meta:
        model = models.Bot
        fields = [
            "user",
            "name",
            "created",
            "bot_zip",
            "bot_zip_updated",
            "bot_zip_publicly_downloadable",
            "bot_data_enabled",
            "bot_data",
            "bot_data_publicly_downloadable",
            "type",
        ]
        filterset_class = BotFilterSet
        connection_class = CountingConnection

    @staticmethod
    def resolve_url(root: models.Bot, info, **args):
        return root.get_absolute_url

    @staticmethod
    def resolve_competition_participations(root: models.Bot, info, **args):
        return root.competition_participations.order_by("-competition__date_created")

    @staticmethod
    def resolve_wiki_article(root: models.Bot, info, **args):
        return root.get_wiki_article().current_revision.content

    @staticmethod
    def resolve_match_participations(root: models.Bot, info, **args):
        return root.matchparticipation_set.all()

    @staticmethod
    def resolve_plays_race(root: models.Bot, info, **args):
        return root.plays_race


class CompetitionParticipationType(DjangoObjectTypeWithUID):
    trend = graphene.Int()

    class Meta:
        model = models.CompetitionParticipation
        fields = [
            "competition",
            "match_count",
            "win_perc",
            "win_count",
            "loss_perc",
            "loss_count",
            "crash_perc",
            "crash_count",
            "highest_elo",
            "elo",
            "division_num",
            "bot",
            "active",
        ]
        filter_fields = []

    @staticmethod
    def resolve_trend(root: models.CompetitionParticipation, info, **args):
        trend_data = models.CompetitionParticipation.objects.filter(id=root.id).calculate_trend(root.competition)
        if trend_data:
            return trend_data[0].trend
        return 0


class CompetitionRoundsType(DjangoObjectTypeWithUID):
    class Meta:
        model = models.Round
        fields = [
            "number",
            "started",
            "finished",
            "complete",
        ]


class CompetitionMapsType(DjangoObjectTypeWithUID):
    download_link = graphene.String()

    class Meta:
        model = models.Map
        fields = [
            "name",
            "file",
        ]

    # *Required* FILE PATH FOR MAP DOWNLOAD FEATURE
    # @staticmethod
    # def resolve_download_link(root: models.Map, info, **args):
    #     return models.map.obtain_s3_filehash_or_default(root.file)
    #


class CompetitionType(DjangoObjectTypeWithUID):
    url = graphene.String()
    participants = DjangoConnectionField("aiarena.graphql.CompetitionParticipationType")
    rounds = DjangoConnectionField("aiarena.graphql.CompetitionRoundsType")
    maps = DjangoConnectionField("aiarena.graphql.CompetitionMapsType")

    class Meta:
        model = models.Competition
        fields = [
            "name",
            "type",
            "date_created",
            "date_opened",
            "date_closed",
            "status",
        ]
        filter_fields = ["status"]
        connection_class = CountingConnection

    @staticmethod
    def resolve_url(root: models.Competition, info, **args):
        return root.get_absolute_url()

    @staticmethod
    def resolve_participants(root: models.Competition, info, **args):
        return Ladders.get_competition_display_full_rankings(root).calculate_trend(root)


class NewsType(DjangoObjectTypeWithUID):
    class Meta:
        model = models.News
        fields = [
            "created",
            "title",
            "text",
            "yt_link",
        ]
        filter_fields = []
        connection_class = CountingConnection


class ViewerType(graphene.ObjectType):
    # This is the private viewer user type.
    # Put data only the logged in user should be able view here.

    user = graphene.Field("aiarena.graphql.UserType")
    api_token = graphene.String()
    email = graphene.String()
    active_bots_limit = graphene.Int()
    request_matches_limit = graphene.Int()
    request_matches_count_left = graphene.Int()
    requested_matches = DjangoConnectionField("aiarena.graphql.MatchType")

    @staticmethod
    def resolve_user(root: models.User, info, **args):
        return root

    @staticmethod
    def resolve_api_token(root: models.User, info):
        return Token.objects.get(user=info.context.user)

    @staticmethod
    def resolve_email(root: models.User, info):
        return root.email

    @staticmethod
    def resolve_active_bots_limit(root: models.User, info, **args):
        return SupporterBenefits.get_active_bots_limit(root)

    @staticmethod
    def resolve_request_matches_limit(root: models.User, info, **args):
        return SupporterBenefits.get_requested_matches_limit(root)

    @staticmethod
    def resolve_request_matches_count_left(root: models.User, info, **args):
        return MatchRequests.get_user_match_request_count_left(root)

    @staticmethod
    def resolve_requested_matches(root: models.User, info, **args):
        return root.requested_matches.order_by("-first_started")


class MatchParticipationFilterSet(FilterSet):
    order_by = OrderingFilter(fields=["match__started", "result"])

    class Meta:
        model = models.MatchParticipation
        fields = ["order_by"]


class MatchParticipationType(DjangoObjectTypeWithUID):
    class Meta:
        model = models.MatchParticipation
        fields = ["elo_change", "avg_step_time", "result", "bot", "match"]
        filterset_class = MatchParticipationFilterSet
        connection_class = CountingConnection


class MatchType(DjangoObjectTypeWithUID):
    participant1 = graphene.Field("aiarena.graphql.BotType")
    participant2 = graphene.Field("aiarena.graphql.BotType")
    status = graphene.String()
    result = graphene.Field("aiarena.graphql.ResultType")

    class Meta:
        model = models.Match
        fields = [
            "result",
            "map",
            "created",
            "started",
            "first_started",
            "requested_by",
        ]
        filter_fields = []
        connection_class = CountingConnection

    @staticmethod
    def resolve_participant1(root: models.Match, info, **args):
        return root.participant1.bot

    @staticmethod
    def resolve_participant2(root: models.Match, info, **args):
        return root.participant2.bot

    @staticmethod
    def resolve_status(root: models.Match, info, **args):
        return root.status

    @staticmethod
    def resolve_result(root: models.Match, info, **args):
        return root.result


class ResultType(DjangoObjectTypeWithUID):
    class Meta:
        model = models.Result
        fields = [
            "winner",
            "type",
            "created",
            "replay_file",
            "game_steps",
            "submitted_by",
        ]
        filter_fields = []
        connection_class = CountingConnection


class Query(graphene.ObjectType):
    node = graphene.relay.Node.Field()
    viewer = graphene.Field("aiarena.graphql.ViewerType")
    competitions = DjangoFilterConnectionField("aiarena.graphql.CompetitionType")
    bots = DjangoFilterConnectionField("aiarena.graphql.BotType")
    news = DjangoFilterConnectionField("aiarena.graphql.NewsType")
    users = DjangoFilterConnectionField("aiarena.graphql.UserType")

    @staticmethod
    def resolve_viewer(root, info, **args):
        if info.context.user.is_authenticated:
            return info.context.user
        return None

    @staticmethod
    def resolve_bots(root, info, **args):
        return models.Bot.objects.all()

    @staticmethod
    def resolve_competitions(root, info, **args):
        return models.Competition.objects.all()

    @staticmethod
    def resolve_news(root, info, **args):
        return models.News.objects.all().order_by("-created")

    @staticmethod
    def resolve_users(root, info, **args):
        return models.User.objects.all()
