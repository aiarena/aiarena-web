import React from "react";
import { graphql, useLazyLoadQuery } from "react-relay";
import { Suspense } from "react";
import { getBase64FromID } from "@/_lib/relayHelpers";
import LoadingSpinner from "@/_components/_display/LoadingSpinnerGray";

import EloChart from "../EloChart";
import Summary from "../Summary";
import FetchError from "@/_components/_display/FetchError";
import { useParams } from "react-router";
import { EloGraphQuery } from "./__generated__/EloGraphQuery.graphql";

// type ActiveTopTab = "elograph" | "winsbytime" | "winsbyrace";

export default function EloGraph() {
  const { id } = useParams<{ id: string }>();
  const data = useLazyLoadQuery<EloGraphQuery>(
    graphql`
      query EloGraphQuery($id: ID!) {
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
            elo
            ...EloChart_node
            ...WinsByTimeChart_node
            ...RaceMatchupChart_node
            ...Summary_node
          }
        }
        viewer {
          user {
            patreonLevel
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
          <div className="flex flex-col gap-4">
            <>
              <EloChart data={data.node} />
              <Summary data={data.node} />
            </>
          </div>
        ) : (
          <div className="text-center py-12">
            <p className="text-gray-400">Competition participation not found</p>
          </div>
        )}
      </div>
    </Suspense>
  );
}
