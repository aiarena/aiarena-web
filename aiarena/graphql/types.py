import graphene
from django_filters import FilterSet, OrderingFilter
from graphene_django import DjangoConnectionField
from graphene_django.filter import DjangoFilterConnectionField

from aiarena.core import models
from aiarena.core.services import Ladders

from aiarena.graphql.common import CountingConnection, DjangoObjectTypeWithUID


class UserType(DjangoObjectTypeWithUID):
    active_bots_limit = graphene.Int()
    request_matches_limit = graphene.Int()
    request_matches_count_left = graphene.Int()
    own_bots = DjangoFilterConnectionField("aiarena.graphql.BotType")

    class Meta:
        model = models.User
        fields = [
            "id",
            "username",
            "email",
            "patreon_level",
            "date_joined",
        ]
        filter_fields = []

    @staticmethod
    def resolve_active_bots_limit(root: models.User, info, **args):
        return models.User.get_active_bots_limit(root)

    @staticmethod
    def resolve_request_matches_limit(root: models.User, info, **args):
        return root.requested_matches_limit

    @staticmethod
    def resolve_request_matches_count_left(root: models.User, info, **args):
        return root.match_request_count_left

    @staticmethod
    def resolve_own_bots(root: models.User, info, **args):
        return root.bots.all()


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

    class Meta:
        model = models.Bot
        fields = [
            "user",
            "name",
            "created",
            "bot_data_enabled",
            "bot_zip_updated",
            "bot_data_publicly_downloadable",
            "plays_race",
            "type",
            "wiki_article",
        ]
        filterset_class = BotFilterSet
        connection_class = CountingConnection

    @staticmethod
    def resolve_url(root: models.Bot, info, **args):
        return root.get_absolute_url

    @staticmethod
    def resolve_competition_participations(root: models.Bot, info, **args):
        return root.competition_participations.all()


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
        ]
        filter_fields = []

    @staticmethod
    def resolve_trend(root: models.CompetitionParticipation, info, **args):
        return root.trend


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


class Query(graphene.ObjectType):
    node = graphene.relay.Node.Field()
    viewer = graphene.Field("aiarena.graphql.UserType")
    competitions = DjangoFilterConnectionField("aiarena.graphql.CompetitionType")
    bots = DjangoFilterConnectionField("aiarena.graphql.BotType")
    news = DjangoFilterConnectionField("aiarena.graphql.NewsType")

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
