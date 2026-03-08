import RankingsSection from "./RankingsSection";
import { useParams } from "react-router";
import { graphql, useLazyLoadQuery } from "react-relay";
import { CompetitionRankingQuery } from "./__generated__/CompetitionRankingQuery.graphql";
import { getBase64FromID } from "@/_lib/relayHelpers";
import FetchError from "@/_components/_display/FetchError";

export default function CompetitionRankings() {
  const { competitionId } = useParams<{ competitionId: string }>();

  const rankings = useLazyLoadQuery<CompetitionRankingQuery>(
    graphql`
      query CompetitionRankingQuery($id: ID!) {
        node(id: $id) {
          ... on CompetitionType {
            ...RankingsSection_competition
          }
        }
      }
    `,
    { id: getBase64FromID(competitionId!, "CompetitionType") || "" },
  );

  if (!rankings.node) {
    return <FetchError type="rankings" />;
  }

  return rankings.node ? (
    <RankingsSection competition={rankings.node} />
  ) : (
    <p>No rankings yet...</p>
  );
}
