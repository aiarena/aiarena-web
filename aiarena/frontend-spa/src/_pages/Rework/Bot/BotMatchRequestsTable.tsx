import { useCallback } from "react";
import { graphql, usePaginationFragment } from "react-relay";

import { getNodes } from "@/_lib/relayHelpers";
import MatchRequestsTable, {
  MatchRequestsQueryVars,
} from "@/_components/_display/MatchRequestsTable";
import { BotMatchRequestsTable_bot$key } from "./__generated__/BotMatchRequestsTable_bot.graphql";

interface BotMatchRequestsTableProps {
  bot: BotMatchRequestsTable_bot$key;
}

export default function BotMatchRequestsTable(
  props: BotMatchRequestsTableProps,
) {
  const { data, loadNext, hasNext, refetch } = usePaginationFragment(
    graphql`
      fragment BotMatchRequestsTable_bot on BotType
      @refetchable(queryName: "BotMatchRequestsTablePaginationQuery")
      @argumentDefinitions(
        cursor: { type: "String" }
        first: { type: "Int", defaultValue: 50 }
        orderBy: { type: "String" }
        showEveryonesTags: { type: "Boolean", defaultValue: false }
      ) {
        requestedMatches(
          first: $first
          after: $cursor
          orderBy: $orderBy
          showEveryonesTags: $showEveryonesTags
        ) @connection(key: "BotMatchRequestsTable_bot_requestedMatches") {
          edges {
            node {
              ...MatchRequestsTable_matches
            }
          }
        }
      }
    `,
    props.bot,
  );

  const refetchMatches = useCallback(
    (vars: MatchRequestsQueryVars) =>
      refetch(vars, { fetchPolicy: "network-only" }),
    [refetch],
  );

  return (
    <MatchRequestsTable
      matches={getNodes(data.requestedMatches)}
      hasNext={hasNext}
      loadNext={loadNext}
      refetch={refetchMatches}
      columnVisibilityKey="Bot_BotMatchRequestsTable_ColumnVisibility"
      emptyMessage={<p>No matches have been requested with this bot.</p>}
      showRequestedBy
    />
  );
}
