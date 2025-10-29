import { getNodes } from "@/_lib/relayHelpers";
import { graphql, useLazyLoadQuery } from "react-relay";
import { CompetitionParticipantCountQuery } from "./__generated__/CompetitionParticipantCountQuery.graphql";
import { Suspense } from "react";
import LoadingSpinner from "./LoadingSpinnerGray";

interface CompetitionParticipantCountProps {
  competitionId: string;
}
export default function CompetitionParticipantCount(
  props: CompetitionParticipantCountProps
) {
  console.log(props.competitionId);
  const data = useLazyLoadQuery<CompetitionParticipantCountQuery>(
    graphql`
      query CompetitionParticipantCountQuery($id: ID!) {
        competitions(id: $id) {
          edges {
            node {
              participants {
                totalCount
              }
            }
          }
        }
      }
    `,
    { id: props.competitionId }
  );

  return (
    <span className="text-white">
      <Suspense fallback={<LoadingSpinner color="gray" />}>
        {getNodes(data.competitions)[0].participants?.totalCount ?? 0}
      </Suspense>
    </span>
  );
}
