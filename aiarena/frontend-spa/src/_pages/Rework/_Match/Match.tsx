import { graphql, useLazyLoadQuery } from "react-relay";
import { getBase64FromID } from "@/_lib/relayHelpers";
import { useParams } from "react-router";
import { MatchQuery } from "./__generated__/MatchQuery.graphql";
import MatchDecal from "./MatchDecal";
import MatchInfo from "./MatchInfo";
import MatchTagSection from "./MatchTagSection";
import { Suspense } from "react";
import LoadingSpinner from "@/_components/_display/LoadingSpinnerGray";
export default function Match() {
  const { matchId } = useParams<{ matchId: string }>();
  const data = useLazyLoadQuery<MatchQuery>(
    graphql`
      query MatchQuery($id: ID!) {
        node(id: $id) {
          ... on MatchType {
            ...MatchInfo_match
            ...MatchDecal_match
            ...MatchTagSection_match
          }
        }
      }
    `,
    { id: getBase64FromID(matchId!, "MatchType") || "" }
  );

  if (!data.node) return <div>Match not found</div>;

  return (
    <>
      <div className="max-w-7xl mx-auto">
        <Suspense fallback={<LoadingSpinner color="light-gray" />}>
          <MatchDecal match={data.node} />
        </Suspense>
        <Suspense fallback={<LoadingSpinner color="light-gray" />}>
          <MatchInfo match={data.node} />
        </Suspense>
        <Suspense fallback={<LoadingSpinner color="light-gray" />}>
          <MatchTagSection match={data.node} />
        </Suspense>
      </div>
    </>
  );
}
