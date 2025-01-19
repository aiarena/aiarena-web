from aiarena.core.tests.base import GraphQLTest
from aiarena.graphql import BotType


class TestUpdateBot(GraphQLTest):
    mutation = """
        mutation($input: UpdateBotInput!) {
            updateBot(input: $input) {
                bot {
                    id
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
            input={
                "id": self.to_global_id(BotType, bot.id),
                "botZipPubliclyDownloadable": True,
                "botDataEnabled": True,
                "botDataPubliclyDownloadable": True,
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

        response = self.mutate(
            login_user=other_user,
            input={
                "id": self.to_global_id(BotType, bot.id),
                "botZipPubliclyDownloadable": True,
            },
        )
        self.assert_graphql_error_like(response, "This is not your bot")

        # Verify bot was not updated
        bot.refresh_from_db()
        assert bot.bot_zip_publicly_downloadable is False

    def test_update_bot_unauthenticated(self, bot):
        """
        Test updating a bot without being authenticated.
        """
        # We expect the bot fixture to be created with those values
        assert bot.bot_zip_publicly_downloadable is False

        response = self.mutate(
            input={
                "id": self.to_global_id(BotType, bot.id),
                "botZipPubliclyDownloadable": True,
            },
        )
        self.assert_graphql_error_like(response, "You are not signed in")

        # Optionally, verify bot was not updated
        bot.refresh_from_db()
        assert bot.bot_zip_publicly_downloadable is False
