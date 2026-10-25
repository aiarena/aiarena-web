from django.conf import settings

from discord_bind.models import DiscordUser

from aiarena.core.tests.base import GraphQLTest


class TestViewerActiveBotParticipations(GraphQLTest):
    """Linking a Discord account adds a bonus to the active participation limit."""

    # language=graphql
    query_text = """
        query {
            viewer {
                activeBotParticipationLimit
                activeBotParticipationDiscordBonus
                linkedDiscord
            }
        }
    """

    def test_without_discord(self, user):
        viewer = self.query(self.query_text, login_user=user)["viewer"]

        assert viewer["linkedDiscord"] is False
        assert viewer["activeBotParticipationDiscordBonus"] == settings.MAX_USER_BOT_PARTICIPATIONS_ACTIVE_DISCORD_BONUS
        assert viewer["activeBotParticipationLimit"] == settings.MAX_USER_BOT_PARTICIPATIONS_ACTIVE_FREE_TIER

    def test_with_discord(self, user):
        DiscordUser.objects.create(user=user, uid="1234", username="discorduser", discriminator="0001")

        viewer = self.query(self.query_text, login_user=user)["viewer"]

        assert viewer["linkedDiscord"] is True
        assert viewer["activeBotParticipationLimit"] == (
            settings.MAX_USER_BOT_PARTICIPATIONS_ACTIVE_FREE_TIER
            + settings.MAX_USER_BOT_PARTICIPATIONS_ACTIVE_DISCORD_BONUS
        )
