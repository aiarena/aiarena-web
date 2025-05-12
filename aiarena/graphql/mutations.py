from django.contrib.auth import authenticate, login, logout
from django.core.exceptions import ValidationError

import graphene
from constance import config
from graphene_django.types import ErrorType
from graphene_file_upload.scalars import Upload
from graphql import GraphQLError

from aiarena.core.models.bot import Bot
from aiarena.core.models.bot_race import BotRace
from aiarena.core.models.competition import Competition
from aiarena.core.models.competition_participation import CompetitionParticipation
from aiarena.core.models.map import Map
from aiarena.core.models.map_pool import MapPool
from aiarena.core.services.internal.match_requests import handle_request_matches
from aiarena.graphql.common import (
    CleanedInputMutation,
    CleanedInputType,
    raise_for_access,
    raise_graphql_error_from_exception,
)
from aiarena.graphql.types import (
    BotType,
    CompetitionParticipationType,
    CompetitionType,
    MapPoolType,
    MapType,
    MatchType,
)


# if we have a method of displaying a meaningful errormessage if incorrect enum is supplied, this would be better
# class MapSelectionTypeEnum(graphene.Enum):
#     specific_map = "specific_map"
#     map_pool = "map_pool"


class RequestMatchInput(CleanedInputType):
    bot1: Bot = graphene.ID()
    bot2: Bot = graphene.ID()
    match_count = graphene.Int()
    # map_selection_type = MapSelectionTypeEnum()
    map_selection_type = graphene.String()
    map_pool: MapPool = graphene.ID(default=None)
    chosen_map: Map = graphene.ID(default=None)

    class Meta:
        required_fields = [
            "bot1",
            "bot2",
            "match_count",
            "map_selection_type",
        ]

    def clean(self, info):
        if not self.map_pool and not self.chosen_map:
            raise GraphQLError("Either 'mapPool' or 'chosenMap' must be provided.")

        if self.map_selection_type != "specific_map" and self.map_selection_type != "map_pool":
            raise GraphQLError("'mapSelectionType' must be set to 'specific_map' or 'map_pool'.")

        if self.map_selection_type == "specific_map" and not self.chosen_map:
            raise GraphQLError("If 'mapSelectionType' is set to 'specific_map', a 'chosenMap' must be provided.")

        if self.map_selection_type == "map_pool" and not self.map_pool:
            raise GraphQLError("If 'mapSelectionType' is set to 'map_pool', a 'mapPool' must be provided.")

    @staticmethod
    def clean_bot1(bot, info):
        try:
            return graphene.Node.get_node_from_global_id(info=info, global_id=bot, only_type=BotType)
        except Exception as e:
            raise GraphQLError(f"Error processing bot1: {str(e)}")

    @staticmethod
    def clean_bot2(bot, info):
        try:
            return graphene.Node.get_node_from_global_id(info=info, global_id=bot, only_type=BotType)
        except Exception as e:
            raise GraphQLError(f"Error processing bot2: {str(e)}")

    @staticmethod
    def clean_map_pool(map_pool, info):
        try:
            return graphene.Node.get_node_from_global_id(info=info, global_id=map_pool, only_type=MapPoolType)
        except Exception as e:
            raise GraphQLError(f"Error processing mapPool: {str(e)}")

    @staticmethod
    def clean_chosen_map(map, info):
        try:
            return graphene.Node.get_node_from_global_id(info=info, global_id=map, only_type=MapType)
        except Exception as e:
            raise GraphQLError(f"Error processing chosenMap: {str(e)}")


class RequestMatch(CleanedInputMutation):
    match = graphene.List(MatchType)

    class Meta:
        input_class = RequestMatchInput

    @classmethod
    def perform_mutate(cls, info: graphene.ResolveInfo, input_object: RequestMatchInput):
        if not info.context.user.is_authenticated:
            raise GraphQLError("You need to be logged in in to perform this action.")

        try:
            matches = handle_request_matches(
                requested_by_user=info.context.user,
                bot1=input_object.bot1,
                opponent=input_object.bot2,
                match_count=input_object.match_count,
                matchup_race=None,
                matchup_type="specific_matchup",
                map_selection_type=input_object.map_selection_type,
                map_pool=input_object.map_pool,
                chosen_map=input_object.chosen_map,
            )

            return cls(errors=[], match=matches)

        except Exception as e:
            raise GraphQLError(f"Error requesting match: {str(e)}")


class UpdateCompetitionParticipationInput(CleanedInputType):
    bot: Bot = graphene.ID()
    competition: Competition = graphene.ID()
    active = graphene.Boolean(default=True)

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
            raise GraphQLError("This competition is closed.")
        return competition


class UpdateCompetitionParticipation(CleanedInputMutation):
    competition_participation = graphene.Field(CompetitionParticipationType)

    class Meta:
        input_class = UpdateCompetitionParticipationInput

    @classmethod
    def get_competition_participation_if_exists(cls, input_object):
        try:
            return input_object.competition.participations.get(bot=input_object.bot)
        except CompetitionParticipation.DoesNotExist:
            return None

    @classmethod
    def create_new_competition_participation(cls, input_object):
        competition_participation = CompetitionParticipation(
            competition=input_object.competition,
            bot=input_object.bot,
            active=input_object.active,
        )
        return competition_participation

    @classmethod
    def update_competition_participation(cls, input_object, competition_participation):
        try:
            competition_participation.active = input_object.active
            competition_participation.full_clean()
            competition_participation.save()
            return competition_participation

        except ValidationError as e:
            raise_graphql_error_from_exception(e)

    @classmethod
    def perform_mutate(cls, info: graphene.ResolveInfo, input_object: UpdateCompetitionParticipationInput):
        raise_for_access(info, input_object.bot)

        competition_participation = cls.get_competition_participation_if_exists(input_object)

        # Return the object if not change to active.
        if competition_participation and competition_participation.active == input_object.active:
            return cls(errors=[], competition_participation=competition_participation)

        # Reset division for existing participant when setting false,
        # or raise error for attempting to set a new competition_participation to false.
        if competition_participation and input_object.active is False:
            competition_participation.division_num = CompetitionParticipation.DEFAULT_DIVISION

        if not competition_participation:
            competition_participation = cls.create_new_competition_participation(input_object)

        competition_participation = cls.update_competition_participation(input_object, competition_participation)

        return cls(errors=[], competition_participation=competition_participation)


class UploadBotInput(CleanedInputType):
    name = graphene.String()
    bot_data_enabled = graphene.Boolean(default=False)
    bot_zip = Upload()
    plays_race = graphene.String()
    type = graphene.String()

    class Meta:
        required_fields = ["name", "bot_zip", "plays_race", "type"]

    @staticmethod
    def clean_plays_race(plays_race, info):
        input_value = plays_race.strip().upper()
        try:
            return BotRace.objects.get(label=input_value)
        except Exception:
            raise ValidationError(f"Invalid bot race: '{plays_race}'")

    @staticmethod
    def clean_type(type, info):
        input_value = type.strip().lower()
        if input_value not in dict(Bot.TYPES):
            raise ValidationError(f"Invalid bot type: '{type}'")
        return input_value


class UploadBot(CleanedInputMutation):
    bot = graphene.Field(BotType)

    class Meta:
        input_class = UploadBotInput

    @classmethod
    def perform_mutate(cls, info: graphene.ResolveInfo, input_object: UploadBotInput):
        if not config.BOT_UPLOADS_ENABLED and getattr(input_object, "bot_zip", None):
            raise Exception("Bot uploads are currently disabled.")

        bot = Bot(
            user=info.context.user,
            name=input_object.name,
            bot_zip=input_object.bot_zip,
            bot_data_enabled=input_object.bot_data_enabled,
            plays_race=input_object.plays_race,
            type=input_object.type,
        )
        try:
            bot.full_clean()
            bot.save()
        except ValidationError as e:
            raise_graphql_error_from_exception(e)

        return cls(errors=[], bot=bot)


class UpdateBotInput(CleanedInputType):
    id = graphene.ID()
    bot_zip_publicly_downloadable = graphene.Boolean()
    bot_data_enabled = graphene.Boolean()
    bot_data_publicly_downloadable = graphene.Boolean()
    wiki_article = graphene.String()
    bot_zip = Upload()

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

        if not config.BOT_UPLOADS_ENABLED and getattr(input_object, "bot_zip", None):
            raise Exception("Bot uploads are currently disabled.")

        for attr, value in input_object.items():
            if attr in ["id", "wiki_article"]:
                continue
            setattr(bot, attr, value)

        if input_object.wiki_article:
            Bot.update_bot_wiki_article(bot, input_object.wiki_article, info.context)
        try:
            bot.full_clean()
            bot.save()

        except ValidationError as e:
            raise_graphql_error_from_exception(e)

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
    request_match = RequestMatch.Field()
    upload_bot = UploadBot.Field()
    update_bot = UpdateBot.Field()
    update_competition_participation = UpdateCompetitionParticipation.Field()
    password_sign_in = PasswordSignIn.Field()
    sign_out = SignOut.Field()
