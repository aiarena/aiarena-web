from aiarena.core.tests.base import GraphQLTest
from aiarena.graphql import CompetitionParticipationType


class TestEloChartData(GraphQLTest):
    # language=graphql
    query_text = """
        query ($id: ID!) {
            node(id: $id) {
                ... on CompetitionParticipationType {
                    eloChartData {
                        lastUpdated
                        data { datasets { label } }
                        roundStarts { number }
                    }
                }
            }
        }
    """

    def test_participation_without_elo_history_returns_empty_chart(self, competition_participation_user):
        # A freshly joined bot has no Elo history yet; this used to crash with
        # an UnboundLocalError instead of returning an empty chart.
        data = self.query(
            self.query_text,
            variables={"id": self.to_global_id(CompetitionParticipationType, competition_participation_user.id)},
        )

        assert data["node"]["eloChartData"] == {
            "lastUpdated": None,
            "data": {"datasets": []},
            "roundStarts": None,
        }
