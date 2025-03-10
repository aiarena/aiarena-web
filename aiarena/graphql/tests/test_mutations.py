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
        assert bot.get_wiki_article().current_revision.content == ""

        self.mutate(
            login_user=user,
            expected_status=200,
            variables={
                "input": {
                    "id": self.to_global_id(BotType, bot.id),
                    "botZipPubliclyDownloadable": True,
                    "botDataEnabled": True,
                    "botDataPubliclyDownloadable": True,
                    "wikiArticle": "#1Some Content"
                }
            },
        )

        # Verify bot was updated correctly
        bot.refresh_from_db()
        assert bot.bot_zip_publicly_downloadable is True
        assert bot.bot_data_enabled is True
        assert bot.bot_data_publicly_downloadable is True
        assert bot.get_wiki_article().current_revision.content == "#1Some Content"

    def test_update_bot_unauthorized(self, user, other_user, bot):
        """
        Test updating a bot that does not belong to the user.
        """
        # We expect the bot fixture to be created with those values
        assert bot.user == user
        assert bot.bot_zip_publicly_downloadable is False
        assert bot.get_wiki_article().current_revision.content == ""
    
        self.mutate(
            login_user=other_user,
            variables={
                "input": {
                    "id": self.to_global_id(BotType, bot.id),
                    "botZipPubliclyDownloadable": True,
                    "wikiArticle": "Some Content"
                }
            },
            expected_errors_like=['bobby cannot perform "write" on "My Bot"'],
        )

        # Verify bot was not updated
        bot.refresh_from_db()
        assert bot.bot_zip_publicly_downloadable is False
        assert bot.get_wiki_article().current_revision.content == ""

    def test_update_bot_unauthenticated(self, bot):
        """
        Test updating a bot without being authenticated.
        """
        # We expect the bot fixture to be created with those values
        assert bot.bot_zip_publicly_downloadable is False
        assert bot.get_wiki_article().current_revision.content == ""

        self.mutate(
            variables={
                "input": {
                    "id": self.to_global_id(BotType, bot.id),
                    "botZipPubliclyDownloadable": True,
                    "wikiArticle": "Some Content"
                }
            },
            expected_errors_like=['AnonymousUser cannot perform "write" on "My Bot"'],
        )

        # Verify bot was not updated
        bot.refresh_from_db()
        assert bot.bot_zip_publicly_downloadable is False
        assert bot.get_wiki_article().current_revision.content == ""

    def test_required_field_not_specified(self, user, bot):
        """
        Test omitting a required field when updating the bot.
        """
        self.mutate(
            login_user=user,
            variables={
                "input": {
                    "botZipPubliclyDownloadable": True,
                    "wikiArticle": "Some Content"
                }
            },
            expected_validation_errors={"id": ["Required field"]},
        )

        # Verify bot was not updated
        bot.refresh_from_db()
        assert bot.bot_zip_publicly_downloadable is False
        assert bot.get_wiki_article().current_revision.content == ""

    def test_cannot_specify_attributes_not_in_input(self, user, bot):
        """
        Test that adding an extra field to the input results in an error.
        """
        self.mutate(
            login_user=user,
            variables={
                "input": {
                    "id": self.to_global_id(BotType, bot.id),
                    "name": "new name pls",
                }
            },
            expected_status=400,
            expected_errors_like=[
                "Field 'name' is not defined by type 'UpdateBotInput'.",
            ],
        )

        # Verify bot was not updated
        bot.refresh_from_db()
        assert bot.bot_zip_publicly_downloadable != "new name pls"
