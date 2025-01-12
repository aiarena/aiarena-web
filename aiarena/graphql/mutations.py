from django.contrib.auth import authenticate, login, logout

import graphene
from graphene_django.types import ErrorType
from graphql import GraphQLError

from aiarena.graphql.common import CleanedInputMutation, CleanedInputType, raise_if_annonymous_user
from aiarena.graphql.types import BotType


class UpdateBotInput(CleanedInputType):
    name = graphene.String()
    id = graphene.ID()
    bot_zip_publicly_downloadable = graphene.Boolean()
    bot_data_enabled = graphene.Boolean()
    bot_data_publicly_downloadable = graphene.Boolean()

class UpdateBot(CleanedInputMutation):
    bot = graphene.Field(BotType)

    class Meta:
        input_class = UpdateBotInput

    @classmethod
    def perform_mutate(cls, info: graphene.ResolveInfo, input_object: UpdateBotInput): 
        raise_if_annonymous_user(info=info)

        bot = graphene.Node.get_node_from_global_id(info=info, global_id=input_object.id, only_type=BotType)
        if bot.user.id != info.context.user.id:
            raise GraphQLError("This is not your bot")
        
        for attr, value in input_object.items():
            if attr == "id":
                continue
            setattr(bot, attr, value)
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
