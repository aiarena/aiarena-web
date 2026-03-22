# =============================================================================
# If there are any changes made to this file, run the following in the
# development environment to generate a new schema:
#
#     python manage.py graphql_schema
#
# (This step happens in CI/CD too.)
# =============================================================================

from django.contrib.auth import authenticate, login, logout
from django.core.exceptions import ValidationError
from django.db import transaction

import graphene
from constance import config
from graphene_django.types import ErrorType
from graphene_file_upload.scalars import Upload
from graphql import GraphQLError

from aiarena.api.arenaclient.common.ac_coordinator import ACCoordinator
from aiarena.api.arenaclient.common.exceptions import LadderDisabled
from aiarena.api.arenaclient.common.result_submission_handler import process_competition_result, update_match_tags
from aiarena.core.exceptions import BotUploadsDisabled, CompetitionClosed, CompetitionClosing, MatchRequestException
from aiarena.core.models import Match, Result, TemporaryUpload
from aiarena.core.models.bot import Bot
from aiarena.core.models.bot_race import BotRace
from aiarena.core.models.competition import Competition
from aiarena.core.models.competition_participation import CompetitionParticipation
from aiarena.core.services import bots, supporters
from aiarena.core.services.service_implementations.internal.match_requests import handle_request_matches
from aiarena.graphql.common import (
    CleanedInputMutation,
    CleanedInputType,
    join_deep_errors_to_string,
    raise_for_access,
)
from aiarena.graphql.types import (
    BotID,
    BotType,
    CompetitionID,
    CompetitionParticipationType,
    MapID,
    MapPoolID,
    MatchID,
    MatchType,
    ResultType,
    TemporaryUploadID,
    TemporaryUploadType,
)


class RequestMatchInput(CleanedInputType):
    bot1 = BotID()
    bot2 = BotID()
    match_count = graphene.Int()
    map_selection_type = graphene.String()
    map_pool = MapPoolID(default=None)
    chosen_map = MapID(default=None)

    class Meta:
        required_fields = [
            "bot1",
            "bot2",
            "match_count",
            "map_selection_type",
        ]

    def clean(self, info):
        if not self.map_pool and not self.chosen_map:
            raise ValidationError("Either 'mapPool' or 'chosenMap' must be provided.")

        if self.map_selection_type != "specific_map" and self.map_selection_type != "map_pool":
            raise ValidationError("'mapSelectionType' must be set to 'specific_map' or 'map_pool'.")

        if self.map_selection_type == "specific_map" and not self.chosen_map:
            raise ValidationError("If 'mapSelectionType' is set to 'specific_map', a 'chosenMap' must be provided.")

        if self.map_selection_type == "map_pool" and not self.map_pool:
            raise ValidationError("If 'mapSelectionType' is set to 'map_pool', a 'mapPool' must be provided.")


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
                supporters_service=supporters,
                bots_service=bots,
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

        except MatchRequestException as e:
            raise MatchRequestException(join_deep_errors_to_string(e))


class UpdateCompetitionParticipationInput(CleanedInputType):
    bot = BotID()
    competition = CompetitionID()
    active = graphene.Boolean(default=True)

    class Meta:
        required_fields = ["bot", "competition"]

    @staticmethod
    def clean_competition(competition: Competition, info):
        """Additional validation on the resolved Competition instance."""
        if competition.status in ["closing"]:
            raise CompetitionClosing

        if competition.status in ["closed"]:
            raise CompetitionClosed

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
            raise ValidationError(join_deep_errors_to_string(e))

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
        if not info.context.user.is_authenticated:
            raise GraphQLError("You need to be logged in in to perform this action.")

        if not config.BOT_UPLOADS_ENABLED and getattr(input_object, "bot_zip", None):
            raise GraphQLError("Bot uploads are currently disabled.")

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
            raise ValidationError(join_deep_errors_to_string(e))

        return cls(errors=[], bot=bot)


class UpdateBotInput(CleanedInputType):
    bot = BotID()
    bot_zip_publicly_downloadable = graphene.Boolean()
    bot_data_enabled = graphene.Boolean()
    bot_data_publicly_downloadable = graphene.Boolean()
    wiki_article = graphene.String()
    bot_zip = Upload()
    bot_data = Upload()

    class Meta:
        required_fields = ["bot"]


class UpdateBot(CleanedInputMutation):
    bot = graphene.Field(BotType)

    class Meta:
        input_class = UpdateBotInput

    @classmethod
    def perform_mutate(cls, info: graphene.ResolveInfo, input_object: UpdateBotInput):
        bot = input_object.bot
        raise_for_access(info, bot)

        if not config.BOT_UPLOADS_ENABLED and getattr(input_object, "bot_zip", None):
            raise BotUploadsDisabled

        for attr, value in input_object.items():
            if attr in ["bot", "wiki_article"]:
                continue
            setattr(bot, attr, value)

        if input_object.wiki_article is not None:
            Bot.update_bot_wiki_article(bot, input_object.wiki_article, info.context)
        try:
            bot.full_clean()
            bot.save()

        except ValidationError as e:
            raise ValidationError(join_deep_errors_to_string(e))

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


# =============================================================================
# Arena Client Mutations
# =============================================================================


class GetNextMatch(graphene.Mutation):
    """Get the next match for an arena client to play."""

    match = graphene.Field(MatchType)

    def mutate(self, info: graphene.ResolveInfo) -> "GetNextMatch":
        user = info.context.user
        if not user.is_authenticated:
            raise GraphQLError("Authentication required.")

        if not user.is_arenaclient:
            raise GraphQLError("Only arena clients can get matches.")

        try:
            match = ACCoordinator.next_match(user.arenaclient, only_unfinished_matches=False)
        except LadderDisabled:
            raise GraphQLError("The ladder is currently disabled.")

        return GetNextMatch(match=match)


class RequestUploadUrlsInput(CleanedInputType):
    count: int = graphene.Int(required=True, description="Number of upload URLs to generate (1-10)")

    @staticmethod
    def clean_count(value, info):
        if value < 1 or value > 10:
            raise ValidationError("Count must be between 1 and 10.")
        return value


class UploadUrlType(graphene.ObjectType):
    """A presigned upload URL with its associated temporary upload record."""

    upload = graphene.Field(TemporaryUploadType, required=True)
    upload_url = graphene.String(required=True)


class RequestUploadUrls(CleanedInputMutation):
    """Request presigned URLs for uploading files to S3."""

    class Meta:
        input_class = RequestUploadUrlsInput

    uploads = graphene.List(graphene.NonNull(UploadUrlType), required=True)

    @classmethod
    def perform_mutate(cls, info, input_object: RequestUploadUrlsInput):
        user = info.context.user
        if not user.is_authenticated:
            raise GraphQLError("Authentication required.")
        if not user.is_arenaclient:
            raise GraphQLError("Only arena clients can request upload URLs.")

        uploads = []
        for _ in range(input_object.count):
            upload = TemporaryUpload.create_for_upload(user)
            uploads.append(
                UploadUrlType(
                    upload=upload,
                    upload_url=upload.generate_presigned_put_url(),
                )
            )

        return cls(uploads=uploads, errors=[])


class SubmitResultInput(CleanedInputType):
    """Input for submitting match results."""

    match: Match = MatchID()
    type: str = graphene.String()
    game_steps: int = graphene.Int()
    bot1_avg_step_time: float = graphene.Float()
    bot2_avg_step_time: float = graphene.Float()
    bot1_tags: list[str] = graphene.List(graphene.String)
    bot2_tags: list[str] = graphene.List(graphene.String)
    # File references (TemporaryUpload IDs)
    replay_file: TemporaryUpload | None = TemporaryUploadID()
    arenaclient_log: TemporaryUpload | None = TemporaryUploadID()
    bot1_data: TemporaryUpload | None = TemporaryUploadID()
    bot2_data: TemporaryUpload | None = TemporaryUploadID()
    bot1_log: TemporaryUpload | None = TemporaryUploadID()
    bot2_log: TemporaryUpload | None = TemporaryUploadID()

    class Meta:
        required_fields = [
            "match",
            "type",
            "game_steps",
        ]

    @staticmethod
    def clean_type(value, info):
        valid_types = [t[0] for t in Result.TYPES]
        if value not in valid_types:
            raise ValidationError(f"Invalid result type. Must be one of: {valid_types}")
        return value

    @staticmethod
    def clean_match(match: Match, info):
        user = info.context.user
        if match.assigned_to is None or match.assigned_to != user:
            raise ValidationError("Match is not assigned to this arena client.")
        return match


class SubmitResult(CleanedInputMutation):
    """Submit the result of a match."""

    class Meta:
        input_class = SubmitResultInput

    result = graphene.Field(ResultType)

    @staticmethod
    def _copy_upload(upload: TemporaryUpload | None, file_field) -> None:
        """Copy a temporary upload to a file field if the upload exists."""
        if upload is not None:
            upload.copy_to_file_field(file_field, "")

    @classmethod
    def perform_mutate(cls, info, input_object: SubmitResultInput):
        user = info.context.user
        if not user.is_authenticated:
            raise GraphQLError("Authentication required.")
        if not user.is_arenaclient:
            raise GraphQLError("Only arena clients can submit results.")

        # Lock match and participations to prevent concurrent result submissions
        match = Match.objects.select_for_update().get(id=input_object.match.id)
        p1 = match.matchparticipation_set.select_for_update().select_related("bot").get(participant_number=1)
        p2 = match.matchparticipation_set.select_for_update().select_related("bot").get(participant_number=2)

        # Check after locking (another request may have submitted while we waited)
        if match.result is not None:
            raise GraphQLError("Match already has a result.")

        result = Result(
            match=match,
            type=input_object.type,
            game_steps=input_object.game_steps,
            submitted_by=user,
        )
        cls._copy_upload(input_object.replay_file, result.replay_file)
        cls._copy_upload(input_object.arenaclient_log, result.arenaclient_log)
        result.save()

        result_cause = Result.calculate_result_cause(input_object.type)

        p1.result = p1.calculate_relative_result(input_object.type)
        p1.result_cause = result_cause
        p1.avg_step_time = input_object.bot1_avg_step_time
        cls._copy_upload(input_object.bot1_log, p1.match_log)
        p1.save()

        p2.result = p2.calculate_relative_result(input_object.type)
        p2.result_cause = result_cause
        p2.avg_step_time = input_object.bot2_avg_step_time
        cls._copy_upload(input_object.bot2_log, p2.match_log)
        p2.save()

        match.result = result
        match.save()

        # Update bot data if applicable (capture old paths for cleanup after commit)
        old_bot_data_keys = []
        match_is_requested = match.is_requested
        if p1.use_bot_data and p1.update_bot_data and not match_is_requested and input_object.bot1_data:
            if p1.bot.bot_data:
                old_bot_data_keys.append(p1.bot.bot_data.name)
            cls._copy_upload(input_object.bot1_data, p1.bot.bot_data)
            p1.bot.save()

        if p2.use_bot_data and p2.update_bot_data and not match_is_requested and input_object.bot2_data:
            if p2.bot.bot_data:
                old_bot_data_keys.append(p2.bot.bot_data.name)
            cls._copy_upload(input_object.bot2_data, p2.bot.bot_data)
            p2.bot.save()

        update_match_tags(match, p1.bot.user, p2.bot.user, input_object.bot1_tags, input_object.bot2_tags)
        process_competition_result(result, p1, p2)

        temp_uploads = [
            input_object.replay_file,
            input_object.arenaclient_log,
            input_object.bot1_data,
            input_object.bot2_data,
            input_object.bot1_log,
            input_object.bot2_log,
        ]

        def cleanup():
            # Delete temporary upload S3 objects and DB records
            for upload in temp_uploads:
                if upload is not None:
                    upload.delete_s3_object()
                    upload.delete()
            # Delete old bot_data files that were replaced
            storage = Bot._meta.get_field("bot_data").storage
            for key in old_bot_data_keys:
                storage.delete(key)

        # Clean up after transaction commits. If we started deleting old files, and it fails in the middle,
        # we can no longer go back to the old state (ie we deleted bot data for bot1, but failed when trying to delete
        # bot data for bot2). This will leave orphaned files in S3, but will result in a correct and consistent state
        # in the database overall.
        transaction.on_commit(cleanup)

        return cls(result=result, errors=[])


class Mutation(graphene.ObjectType):
    request_match = RequestMatch.Field()
    upload_bot = UploadBot.Field()
    update_bot = UpdateBot.Field()
    update_competition_participation = UpdateCompetitionParticipation.Field()
    password_sign_in = PasswordSignIn.Field()
    sign_out = SignOut.Field()

    # Arena Client mutations
    request_upload_urls = RequestUploadUrls.Field()
    get_next_match = GetNextMatch.Field()
    submit_result = SubmitResult.Field()
