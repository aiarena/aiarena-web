from aiarena.core.tests.base import GraphQLTest
from aiarena.graphql import BotType


class TestUpdateBot(GraphQLTest):
    mutation_name = "updateBot"
    mutation = """
        mutation($input: UpdateBotInput!) {
            updateBot(input: $input) {
                bot {
                    id
                }
                errors {
                    field
                    messages
                }
            }
        }
    """

    def test_update_bot_success(self, user, bot):
        """
        Test updating a bot with all fields set to True.
        """

        # We expect the bot fixture to be created with those values
        assert bot.user == user
        assert bot.bot_zip_publicly_downloadable is False
        assert bot.bot_data_enabled is False
        assert bot.bot_data_publicly_downloadable is False

        self.mutate(
            login_user=user,
            expected_status=200,
            variables={
                "input": {
                    "id": self.to_global_id(BotType, bot.id),
                    "botZipPubliclyDownloadable": True,
                    "botDataEnabled": True,
                    "botDataPubliclyDownloadable": True,
                }
            },
        )

        # Verify bot was updated correctly
        bot.refresh_from_db()
        assert bot.bot_zip_publicly_downloadable is True
        assert bot.bot_data_enabled is True
        assert bot.bot_data_publicly_downloadable is True

    def test_update_bot_unauthorized(self, user, other_user, bot):
        """
        Test updating a bot that does not belong to the user.
        """
        # We expect the bot fixture to be created with those values
        assert bot.user == user
        assert bot.bot_zip_publicly_downloadable is False

        self.mutate(
            login_user=other_user,
            variables={
                "input": {
                    "id": self.to_global_id(BotType, bot.id),
                    "botZipPubliclyDownloadable": True,
                }
            },
            expected_errors=["This is not your bot"],
        )

        # Verify bot was not updated
        bot.refresh_from_db()
        assert bot.bot_zip_publicly_downloadable is False

    def test_update_bot_unauthenticated(self, bot):
        """
        Test updating a bot without being authenticated.
        """
        # We expect the bot fixture to be created with those values
        assert bot.bot_zip_publicly_downloadable is False

        self.mutate(
            variables={
                "input": {
                    "id": self.to_global_id(BotType, bot.id),
                    "botZipPubliclyDownloadable": True,
                }
            },
            expected_errors=["You are not signed in"],
        )

        # Optionally, verify bot was not updated
        bot.refresh_from_db()
        assert bot.bot_zip_publicly_downloadable is False

    def test_required_field_not_specified(self, user, bot):
        """
        Test updating a bot without being authenticated.
        """
        self.mutate(
            login_user=user,
            variables={
                "input": {
                    "botZipPubliclyDownloadable": True,
                }
            },
            expected_validation_errors={"id": ["Required field"]},
        )

        # Optionally, verify bot was not updated
        bot.refresh_from_db()
        assert bot.bot_zip_publicly_downloadable is False
