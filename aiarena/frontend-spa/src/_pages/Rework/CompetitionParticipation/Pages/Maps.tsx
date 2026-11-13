import { Suspense } from "react";
import { graphql, useLazyLoadQuery } from "react-relay";
import { useParams } from "react-router";

import { getBase64FromID } from "@/_lib/relayHelpers";
import ErrorBoundaryWrapper from "@/_lib/ErrorBoundary";
import FetchError from "@/_components/_display/FetchError";
import DisplaySkeletonTable from "@/_components/_display/_skeletons/DisplaySkeletonTable";
import MapStatsTable from "../MapStatsTable";
import type { MapsQuery } from "./__generated__/MapsQuery.graphql";

export default function Maps() {
  return (
    <div className="px-2 pb-8">
      <Suspense fallback={<DisplaySkeletonTable columns={10} rows={8} />}>
        <ErrorBoundaryWrapper componentName="maps">
          <MapStats />
        </ErrorBoundaryWrapper>
      </Suspense>
    </div>
  );
}

function MapStats() {
  const { id } = useParams<{ id: string }>();

  const data = useLazyLoadQuery<MapsQuery>(
    graphql`
      query MapsQuery($id: ID!) {
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
            ...MapStatsTable_node
          }
        }
      }
    `,
    { id: getBase64FromID(`${id}`, "CompetitionParticipationType") || "" },
  );

  if (!data.node || !data.node.bot) {
    return <FetchError type="competition participation" />;
  }

  return <MapStatsTable data={data.node} />;
}
