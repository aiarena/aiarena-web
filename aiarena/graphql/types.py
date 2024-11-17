import graphene
from django_filters import FilterSet, OrderingFilter
from graphene_django import DjangoConnectionField
from graphene_django.filter import DjangoFilterConnectionField

from aiarena.core import models
from aiarena.core.services import Ladders
from aiarena.graphql.common import CountingConnection, DjangoObjectTypeWithUID


class UserType(DjangoObjectTypeWithUID):
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


class BotFilterSet(FilterSet):
    order_by = OrderingFilter(
        fields=[
            "bot_zip_updated",
        ]
    )

    class Meta:
        model = models.Bot
        fields = ["name", "order_by"]


class BotType(DjangoObjectTypeWithUID):
    url = graphene.String()

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


class CompetitionParticipationType(DjangoObjectTypeWithUID):
    trend = graphene.Int()

    class Meta:
        model = models.CompetitionParticipation
        fields = [
            "elo",
            "division_num",
            "bot",
        ]

    @staticmethod
    def resolve_trend(root: models.CompetitionParticipation, info, **args):
        return root.trend


class CompetitionType(DjangoObjectTypeWithUID):
    url = graphene.String()
    participants = DjangoConnectionField("aiarena.graphql.CompetitionParticipationType")

    class Meta:
        model = models.Competition
        fields = [
            "name",
            "type",
            "game_mode",
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
