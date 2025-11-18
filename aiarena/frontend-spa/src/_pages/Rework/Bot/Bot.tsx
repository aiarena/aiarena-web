import { graphql, useLazyLoadQuery } from "react-relay";
import InformationSection from "./InformationSection";
import { BotQuery } from "./__generated__/BotQuery.graphql";
import { useParams } from "react-router";
import LoadingSpinner from "@/_components/_display/LoadingSpinnerGray";
import { Suspense } from "react";
import { getBase64FromID } from "@/_lib/relayHelpers";
import BotCompetitionsTable from "./BotCompetitionsTable";

export default function Bot() {
  const { botId } = useParams<{ botId: string }>();
  const data = useLazyLoadQuery<BotQuery>(
    graphql`
      query BotQuery($id: ID!) {
        node(id: $id) {
          ... on BotType {
            ...InformationSection_bot
            ...BotCompetitionsTable_bot
          }
        }
      }
    `,
    { id: getBase64FromID(botId!, "BotType") || "" }
  );
  if (!data.node) return <div>Bot not found</div>;
  return (
    <div className="max-w-7xl mx-auto">
      <h4 className="mb-4">Bot information</h4>
      <Suspense fallback={<LoadingSpinner color="light-gray" />}>
        <InformationSection bot={data.node} />
      </Suspense>
      <h4 className="mb-4">Competition Participations</h4>
      <Suspense fallback={<LoadingSpinner color="light-gray" />}>
        <BotCompetitionsTable bot={data.node} />
      </Suspense>
    </div>
  );
}
