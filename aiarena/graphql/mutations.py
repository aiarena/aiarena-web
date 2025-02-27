from django.contrib.auth import authenticate, login, logout

import graphene
from graphene_django.types import ErrorType

from aiarena.core.models.bot import Bot

from aiarena.graphql.common import CleanedInputMutation, CleanedInputType, raise_for_access
from aiarena.graphql.types import BotType


class UpdateBotInput(CleanedInputType):
    id = graphene.ID()
    bot_zip_publicly_downloadable = graphene.Boolean()
    bot_data_enabled = graphene.Boolean()
    bot_data_publicly_downloadable = graphene.Boolean()
    wiki_article_content = graphene.String()
    
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
            if attr in ["id", "wiki_article_content"]: 
                continue
            setattr(bot, attr, value)
            
        if input_object.wiki_article_content:
            Bot.update_bot_wiki_article(bot, input_object.wiki_article_content, info.context)

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
    password_sign_in = PasswordSignIn.Field()
    sign_out = SignOut.Field()
