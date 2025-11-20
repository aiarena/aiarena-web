import { graphql, useLazyLoadQuery } from "react-relay";
import { useParams } from "react-router";
import LoadingSpinner from "@/_components/_display/LoadingSpinnerGray";
import { Suspense } from "react";
import { getBase64FromID } from "@/_lib/relayHelpers";
import CompetitionInformationSection from "./CompetitionInformationSection";
import { CompetitionQuery } from "./__generated__/CompetitionQuery.graphql";
import RankingsSection from "./RankingsSection";
import { CompetitionRankingQuery } from "./__generated__/CompetitionRankingQuery.graphql";
import FetchError from "@/_components/_display/FetchError";

export default function Competition() {
  const { competitionId } = useParams<{ competitionId: string }>();
  const data = useLazyLoadQuery<CompetitionQuery>(
    graphql`
      query CompetitionQuery($id: ID!) {
        node(id: $id) {
          ... on CompetitionType {
            ...CompetitionInformationSection_competition
            ...CompetitionRoundsModal_competition
          }
        }
      }
    `,
    { id: getBase64FromID(competitionId!, "CompetitionType") || "" }
  );

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
    { id: getBase64FromID(competitionId!, "CompetitionType") || "" }
  );
  if (!data.node) {
    return <FetchError type="competition" />;
  }

  if (!rankings.node) {
    return <FetchError type="rankings" />;
  }
  return (
    <div className="max-w-7xl mx-auto">
      <Suspense fallback={<LoadingSpinner color="light-gray" />}>
        <CompetitionInformationSection competiton={data.node} />
      </Suspense>
      <h4 className="mb-4">Rankings</h4>
      <Suspense fallback={<LoadingSpinner color="light-gray" />}>
        {rankings.node ? (
          <RankingsSection competition={rankings.node} />
        ) : (
          <p>No rankings yet...</p>
        )}
      </Suspense>
    </div>
  );
}
