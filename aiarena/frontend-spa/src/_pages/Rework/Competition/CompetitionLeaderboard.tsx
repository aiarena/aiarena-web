import LeaderboardSection from "./LeaderboardSection";
import { useParams } from "react-router";
import { graphql, useLazyLoadQuery } from "react-relay";
import { getBase64FromID } from "@/_lib/relayHelpers";
import FetchError from "@/_components/_display/FetchError";
import { CompetitionLeaderboardQuery } from "./__generated__/CompetitionLeaderboardQuery.graphql";

export default function CompetitionLeaderboard() {
  const { competitionId } = useParams<{ competitionId: string }>();

  const rankings = useLazyLoadQuery<CompetitionLeaderboardQuery>(
    graphql`
      query CompetitionLeaderboardQuery($id: ID!) {
        node(id: $id) {
          ... on CompetitionType {
            ...LeaderboardSection_competition
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
    <LeaderboardSection competition={rankings.node} />
  ) : (
    <p>No rankings yet...</p>
  );
}
