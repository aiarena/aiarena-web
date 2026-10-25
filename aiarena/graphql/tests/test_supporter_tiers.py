from django.conf import settings

from aiarena.core.tests.base import GraphQLTest


class TestSupporterTiers(GraphQLTest):
    # language=graphql
    query_text = """
        query {
            supporterTiers {
                level
                name
                activeBotParticipationLimit
            }
        }
    """

    def test_lists_tiers_cheapest_first(self, user):
        tiers = self.query(self.query_text, login_user=user)["supporterTiers"]

        assert [tier["level"] for tier in tiers] == ["none", "bronze", "silver", "gold", "platinum", "diamond"]
        assert tiers[0] == {
            "level": "none",
            "name": "None",
            "activeBotParticipationLimit": settings.MAX_USER_BOT_PARTICIPATIONS_ACTIVE_FREE_TIER,
        }
        assert tiers[1]["activeBotParticipationLimit"] == settings.MAX_USER_BOT_PARTICIPATIONS_ACTIVE_BRONZE_TIER
