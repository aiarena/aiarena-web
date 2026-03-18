import { graphql, useLazyLoadQuery } from "react-relay";
import { getBase64FromID } from "@/_lib/relayHelpers";
import { useParams } from "react-router";
import { MatchQuery } from "./__generated__/MatchQuery.graphql";
import MatchDecal from "./MatchDecal";
import MatchInfo from "./MatchInfo";
import MatchTagSection from "./MatchTagSection";
import FetchError from "@/_components/_display/FetchError";
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
    { id: getBase64FromID(matchId!, "MatchType") || "" },
  );
  if (!data.node) {
    return <FetchError type="match" />;
  }

  return (
    <>
      <div className="max-w-7xl mx-auto grid gap-8">
        <MatchDecal match={data.node} />
        <MatchInfo match={data.node} />
        <MatchTagSection match={data.node} />
      </div>
    </>
  );
}
