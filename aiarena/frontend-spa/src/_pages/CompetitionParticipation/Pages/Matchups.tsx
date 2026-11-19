import { Suspense } from "react";
import { graphql, useLazyLoadQuery } from "react-relay";
import { useParams } from "react-router";

import { getBase64FromID } from "@/_lib/relayHelpers";
import ErrorBoundaryWrapper from "@/_lib/ErrorBoundary";
import FetchError from "@/_components/_display/FetchError";
import DisplaySkeletonTable from "@/_components/_display/_skeletons/DisplaySkeletonTable";
import MatchupStatsTable from "../MatchupStatsTable";
import type { MatchupsQuery } from "./__generated__/MatchupsQuery.graphql";

export default function Matchups() {
  return (
    <div className="px-2 pb-8">
      <Suspense fallback={<DisplaySkeletonTable columns={11} rows={15} />}>
        <ErrorBoundaryWrapper componentName="matchups">
          <MatchupStats />
        </ErrorBoundaryWrapper>
      </Suspense>
    </div>
  );
}

function MatchupStats() {
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

  return <MatchupStatsTable data={data.node} />;
}
