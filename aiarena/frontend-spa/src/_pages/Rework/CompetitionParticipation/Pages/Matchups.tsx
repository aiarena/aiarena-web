import { graphql, useLazyLoadQuery } from "react-relay";
import { Suspense } from "react";
import { getBase64FromID } from "@/_lib/relayHelpers";
import { MatchupsQuery } from "./__generated__/MatchupsQuery.graphql";
import MatchupStatsTable from "../MatchupStatsTable";
import FetchError from "@/_components/_display/FetchError";
import { useParams } from "react-router";
import DisplaySkeleton from "@/_components/_display/_skeletons/DisplaySkeleton";
import { SkeletonCardShadow } from "@/_components/_display/_skeletons/SkeletonCardShadow";

export default function Matchups() {
  const { id } = useParams<{ id: string }>();
  const data = useLazyLoadQuery<MatchupsQuery>(
    graphql`
      query MatchupsQuery($id: ID!) {
        node(id: $id) {
          ... on CompetitionParticipationType {
            id
            bot {
              id
              name
            }
            competition {
              id
              name
            }
            ...MatchupStatsTable_node
          }
        }
      }
    `,
    { id: getBase64FromID(`${id}`, "CompetitionParticipationType") || "" },
  );
  if (!data.node || !data.node.bot) {
    return <FetchError type="competition participation" />;
  }
  return (
    <div className="px-2 pb-8">
      <Suspense
        fallback={<DisplaySkeleton height={800} styles={SkeletonCardShadow} />}
      >
        {data.node.bot ? (
          <MatchupStatsTable data={data.node} />
        ) : (
          <div className="text-center py-12">
            <p className="text-gray-400">Competition participation not found</p>
          </div>
        )}
      </Suspense>
    </div>
  );
}
