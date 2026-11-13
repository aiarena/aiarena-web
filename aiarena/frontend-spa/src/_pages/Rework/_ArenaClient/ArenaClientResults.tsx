import { useMemo } from "react";
import { graphql, usePaginationFragment } from "react-relay";
import { getCoreRowModel, useReactTable } from "@tanstack/react-table";

import { getNodes } from "@/_lib/relayHelpers";
import { TableContainer } from "@/_components/_actions/TableContainer";
import NoItemsInListMessage from "@/_components/_display/NoItemsInListMessage";
import NoMoreItems from "@/_components/_display/NoMoreItems";
import LoadingMoreItems from "@/_components/_display/LoadingMoreItems";
import { useInfiniteScroll } from "@/_components/_hooks/useInfiniteScroll";
import { readResultRow, useResultColumns } from "@/_components/_display/resultsTable/resultColumns";
import { ArenaClientResults_arenaClient$key } from "./__generated__/ArenaClientResults_arenaClient.graphql";

interface ArenaClientResultsProps {
  arenaClient: ArenaClientResults_arenaClient$key;
}

export default function ArenaClientResults(props: ArenaClientResultsProps) {
  const { data, loadNext, hasNext } = usePaginationFragment(
    graphql`
      fragment ArenaClientResults_arenaClient on ArenaClientType
      @refetchable(queryName: "ArenaClientResultsPaginationQuery")
      @argumentDefinitions(
        cursor: { type: "String" }
        first: { type: "Int", defaultValue: 50 }
      ) {
        results(first: $first, after: $cursor)
          @connection(key: "ArenaClientResults_arenaClient_results") {
          edges {
            node {
              ...resultColumns_result
            }
          }
        }
      }
    `,
    props.arenaClient,
  );

  const rows = useMemo(() => getNodes(data.results).map(readResultRow), [data]);
  const columns = useResultColumns();
  const { loadMoreRef } = useInfiniteScroll(() => loadNext(50), hasNext);

  const table = useReactTable({
    data: rows,
    columns,
    getCoreRowModel: getCoreRowModel(),
    enableColumnResizing: true,
    columnResizeMode: "onChange",
  });

  if (rows.length === 0) {
    return (
      <NoItemsInListMessage>
        <p>This client hasn't played any matches yet.</p>
      </NoItemsInListMessage>
    );
  }

  return (
    <div>
      <TableContainer table={table} loading={false} />
      {hasNext ? (
        <div className="flex justify-center mt-6" ref={loadMoreRef}>
          <LoadingMoreItems loadingMessage="Loading more results..." />
        </div>
      ) : (
        <div className="mt-8">
          <NoMoreItems />
        </div>
      )}
    </div>
  );
}
