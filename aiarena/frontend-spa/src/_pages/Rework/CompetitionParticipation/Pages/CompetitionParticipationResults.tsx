import { Suspense } from "react";
import { graphql, useLazyLoadQuery } from "react-relay";
import { useParams } from "react-router";

import { getBase64FromID } from "@/_lib/relayHelpers";
import FetchError from "@/_components/_display/FetchError";
import DisplaySkeletonTable from "@/_components/_display/_skeletons/DisplaySkeletonTable";
import BotResults from "../../Bot/BotResults";
import { CompetitionParticipationResultsQuery } from "./__generated__/CompetitionParticipationResultsQuery.graphql";

export default function CompetitionParticipationResults() {
  return (
    <div className="px-2 pb-8">
      <Suspense fallback={<DisplaySkeletonTable columns={12} rows={20} />}>
        <ParticipationResults />
      </Suspense>
    </div>
  );
}

function ParticipationResults() {
  const { id } = useParams<{ id: string }>();

  const data = useLazyLoadQuery<CompetitionParticipationResultsQuery>(
    graphql`
      query CompetitionParticipationResultsQuery($id: ID!) {
        node(id: $id) {
          ... on CompetitionParticipationType {
            id
            bot {
              id
              botZipUpdated
            }
            competition {
              id
              name
            }
          }
        }
      }
    `,
    { id: getBase64FromID(`${id}`, "CompetitionParticipationType") || "" },
  );

  if (!data.node || !data.node.bot || !data.node.competition) {
    return <FetchError type="competition participation" />;
  }

  return (
    <BotResults
      origin="competition"
      botId={data.node.bot.id}
      botZipUpdated={data.node.bot.botZipUpdated}
      competition={{
        id: data.node.competition.id,
        name: data.node.competition.name,
      }}
    />
  );
}
