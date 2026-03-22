import { graphql, useLazyLoadQuery } from "react-relay";
import { Suspense } from "react";
import { getBase64FromID } from "@/_lib/relayHelpers";

import Summary from "../Summary";
import FetchError from "@/_components/_display/FetchError";
import { useParams } from "react-router";
import WinsByTimeChart from "../WinsByTime";
import { WinsByTimeQuery } from "./__generated__/WinsByTimeQuery.graphql";
import DisplaySkeleton from "@/_components/_display/_skeletons/DisplaySkeleton";
import { SkeletonCardShadow } from "@/_components/_display/_skeletons/SkeletonCardShadow";
import ErrorBoundaryWrapper from "@/_lib/ErrorBoundary";

export default function WinsByTime() {
  const { id } = useParams<{ id: string }>();
  const data = useLazyLoadQuery<WinsByTimeQuery>(
    graphql`
      query WinsByTimeQuery($id: ID!) {
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
            ...WinsByTimeChart_node
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
    <div className="px-2 pb-8">
      <Suspense
        fallback={<DisplaySkeleton height={800} styles={SkeletonCardShadow} />}
      >
        <ErrorBoundaryWrapper componentName="wins by time">
          {data.node.bot ? (
            <div className="flex flex-col gap-4">
              <>
                <WinsByTimeChart data={data.node} />
                <Summary data={data.node} />
              </>
            </div>
          ) : (
            <div className="text-center py-12">
              <p className="text-gray-400">
                Competition participation not found
              </p>
            </div>
          )}
        </ErrorBoundaryWrapper>
      </Suspense>
    </div>
  );
}
