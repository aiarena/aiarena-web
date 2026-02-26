import { graphql, useLazyLoadQuery } from "react-relay";
import { Suspense } from "react";
import { getBase64FromID } from "@/_lib/relayHelpers";
import LoadingSpinner from "@/_components/_display/LoadingSpinnerGray";

import type { MapsQuery } from "./__generated__/MapsQuery.graphql";
import MapStatsTable from "../MapStatsTable";
import FetchError from "@/_components/_display/FetchError";
import { useParams } from "react-router";

export default function Maps() {
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
  return (
    <Suspense fallback={<LoadingSpinner color="light-gray" />}>
      <div className="px-2 pb-8">
        {data.node.bot ? (
          <MapStatsTable data={data.node} />
        ) : (
          <div className="text-center py-12">
            <p className="text-gray-400">Competition participation not found</p>
          </div>
        )}
      </div>
    </Suspense>
  );
}
