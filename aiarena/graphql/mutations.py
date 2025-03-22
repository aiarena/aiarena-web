from django.contrib.auth import authenticate, login, logout

from django.core.exceptions import ValidationError

import graphene
from graphene_django.types import ErrorType

from aiarena.core.models.competition_participation import CompetitionParticipation
from aiarena.core.models.competition import Competition
from aiarena.core.models.bot import Bot
from aiarena.graphql.common import CleanedInputMutation, CleanedInputType, raise_for_access
from aiarena.graphql.types import BotType, CompetitionParticipationType, CompetitionType


class ToggleCompetitionParticipationInput(CleanedInputType):
    bot: Bot = graphene.ID()
    competition: Competition = graphene.ID()

    class Meta:
        required_fields = ["bot", "competition"]

    @staticmethod
    def clean_bot(bot, info):
        try:
            return graphene.Node.get_node_from_global_id(info=info, global_id=bot, only_type=BotType)
        except Exception as e:
            raise ValidationError(e)

    @staticmethod
    def clean_competition(competition, info):
        try:
            competition: Competition = graphene.Node.get_node_from_global_id(
                info=info, global_id=competition, only_type=CompetitionType
            )
        except Exception as e:
            raise ValidationError(e)

        if competition.status in ["closing", "closed"]:
            raise ValidationError("This competition is closed.")
        return competition


class ToggleCompetitionParticipation(CleanedInputMutation):
    competition_participation = graphene.Field(CompetitionParticipationType)

    class Meta:
        input_class = ToggleCompetitionParticipationInput

    @classmethod
    def perform_mutate(cls, info: graphene.ResolveInfo, input_object: ToggleCompetitionParticipationInput):

        raise_for_access(info, input_object.bot)
        try:
            competition_participation: CompetitionParticipation = input_object.competition.participations.get(
                bot=input_object.bot
            )

        except CompetitionParticipation.DoesNotExist:
            competition_participation = None

        if competition_participation is None:
            competition_participation = input_object.competition.participations.create(bot=input_object.bot)

        elif competition_participation.active:
            competition_participation.division_num = CompetitionParticipation.DEFAULT_DIVISION
            competition_participation.active = False
            competition_participation.save()

        else:
            competition_participation.active = True
            competition_participation.save()

        return cls(errors=[], competition_participation=competition_participation)


class UpdateBotInput(CleanedInputType):
    id = graphene.ID()
    bot_zip_publicly_downloadable = graphene.Boolean()
    bot_data_enabled = graphene.Boolean()
    bot_data_publicly_downloadable = graphene.Boolean()
    wiki_article = graphene.String()

    class Meta:
        required_fields = ["id"]


class UpdateBot(CleanedInputMutation):
    bot = graphene.Field(BotType)

    class Meta:
        input_class = UpdateBotInput

    @classmethod
    def perform_mutate(cls, info: graphene.ResolveInfo, input_object: UpdateBotInput):
        bot = graphene.Node.get_node_from_global_id(info=info, global_id=input_object.id, only_type=BotType)
        raise_for_access(info, bot)

        for attr, value in input_object.items():
            if attr in ["id", "wiki_article"]:
                continue
            setattr(bot, attr, value)

        if input_object.wiki_article:
            Bot.update_bot_wiki_article(bot, input_object.wiki_article, info.context)

        bot.save()

        return cls(errors=[], bot=bot)


class PasswordSignInInput(CleanedInputType):
    username = graphene.String()
    password = graphene.String()


class PasswordSignIn(CleanedInputMutation):
    class Meta:
        input_class = PasswordSignInInput

    @classmethod
    def perform_mutate(cls, info: graphene.ResolveInfo, input_object):
        if user := authenticate(
            username=input_object.username,
            password=input_object.password,
        ):
            login(request=info.context, user=user)
        else:
            return cls(
                errors=[
                    ErrorType(
                        field="__all__",
                        messages=["Incorrect email or password"],
                    )
                ]
            )

        return cls(errors=[])


class SignOut(graphene.Mutation):
    errors = graphene.List(ErrorType)

    def mutate(self, info: graphene.ResolveInfo) -> "SignOut":
        if not info.context.user.is_authenticated:
            return SignOut(
                errors=[
                    ErrorType(
                        field="__all__",
                        messages=["You are not signed in"],
                    )
                ]
            )
        logout(request=info.context)
        return SignOut(errors=[])


class Mutation(graphene.ObjectType):
    update_bot = UpdateBot.Field()
    toggle_competition_participation = ToggleCompetitionParticipation.Field()
    password_sign_in = PasswordSignIn.Field()
    sign_out = SignOut.Field()
