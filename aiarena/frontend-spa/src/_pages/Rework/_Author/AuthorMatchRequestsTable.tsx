import { useCallback } from "react";
import { graphql, usePaginationFragment } from "react-relay";

import { getNodes } from "@/_lib/relayHelpers";
import MatchRequestsTable, {
  MatchRequestsQueryVars,
} from "@/_components/_display/MatchRequestsTable";
import { AuthorMatchRequestsTable_user$key } from "./__generated__/AuthorMatchRequestsTable_user.graphql";

interface AuthorMatchRequestsTableProps {
  data: AuthorMatchRequestsTable_user$key;
}

export default function AuthorMatchRequestsTable(
  props: AuthorMatchRequestsTableProps,
) {
  const { data, loadNext, hasNext, refetch } = usePaginationFragment(
    graphql`
      fragment AuthorMatchRequestsTable_user on UserType
      @refetchable(queryName: "AuthorMatchRequestsTablePaginationQuery")
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
        ) @connection(key: "AuthorMatchRequestsTable_user_requestedMatches") {
          edges {
            node {
              ...MatchRequestsTable_matches
            }
          }
        }
      }
    `,
    props.data,
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
      columnVisibilityKey="Author_AuthorMatchRequestsTable_ColumnVisibility"
      emptyMessage={<p>This author has not requested any matches.</p>}
      loadingMoreMessage="Loading more match requests..."
    />
  );
}
