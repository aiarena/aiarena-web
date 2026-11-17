import { useCallback } from "react";
import { graphql, usePaginationFragment } from "react-relay";

import { getNodes } from "@/_lib/relayHelpers";
import { useRegisterConnectionID } from "@/_components/_hooks/useRegisterRelayConnectionID";
import { CONNECTION_KEYS } from "@/_components/_contexts/RelayConnectionIDContext/RelayConnectionIDKeys";
import MatchRequestsTable, {
  MatchRequestsQueryVars,
} from "@/_components/_display/MatchRequestsTable";
import { UserMatchRequestsTable_viewer$key } from "./__generated__/UserMatchRequestsTable_viewer.graphql";

interface UserMatchRequestsTableProps {
  viewer: UserMatchRequestsTable_viewer$key;
}

export default function UserMatchRequestsTable(
  props: UserMatchRequestsTableProps,
) {
  const { data, loadNext, hasNext, refetch } = usePaginationFragment(
    graphql`
      fragment UserMatchRequestsTable_viewer on Viewer
      @refetchable(queryName: "UserMatchRequestsTablePaginationQuery")
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
        ) @connection(key: "UserMatchRequestsSection_viewer_requestedMatches") {
          __id
          edges {
            node {
              ...MatchRequestsTable_matches
            }
          }
        }
      }
    `,
    props.viewer,
  );

  // The request-match modal inserts newly requested matches into this connection.
  useRegisterConnectionID(
    CONNECTION_KEYS.UserMatchRequestsConnection,
    data?.requestedMatches?.__id,
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
      columnVisibilityKey="UserMatchRequests_UserMatchRequestsTable_ColumnVisibility"
      emptyMessage={<p>Request your first match, and it will show up here.</p>}
      loadingMoreMessage="Loading more match requests..."
    />
  );
}
