import { graphql, useLazyLoadQuery } from "react-relay";

import FetchError from "@/_components/_display/FetchError";
import BotMatchRequestsTable from "./BotMatchRequestsTable";
import { BotMatchRequestsQuery } from "./__generated__/BotMatchRequestsQuery.graphql";

/** Queries on its own, so render it inside the section's Suspense boundary. */
export default function BotMatchRequests({ botId }: { botId: string }) {
  const data = useLazyLoadQuery<BotMatchRequestsQuery>(
    graphql`
      query BotMatchRequestsQuery($id: ID!) {
        node(id: $id) {
          ... on BotType {
            ...BotMatchRequestsTable_bot
          }
        }
      }
    `,
    { id: botId },
  );

  if (!data.node) {
    return <FetchError type="bot" />;
  }

  return <BotMatchRequestsTable bot={data.node} />;
}
