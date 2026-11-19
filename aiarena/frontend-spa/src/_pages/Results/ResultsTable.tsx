import { graphql, usePaginationFragment } from "react-relay";
import {
  getCoreRowModel,
  useReactTable,
  VisibilityState,
} from "@tanstack/react-table";
import { Suspense, useMemo, useState, useTransition } from "react";

import NoItemsInListMessage from "@/_components/_display/NoItemsInListMessage";
import NoMoreItems from "@/_components/_display/NoMoreItems";
import LoadingMoreItems from "@/_components/_display/LoadingMoreItems";
import { TableContainer } from "@/_components/_actions/TableContainer";
import LoadingDots from "@/_components/_display/LoadingDots";
import { useInfiniteScroll } from "@/_components/_hooks/useInfiniteScroll";
import { ResultsTable_node$key } from "./__generated__/ResultsTable_node.graphql";
import { getNodes } from "@/_lib/relayHelpers";
import {
  readResultRow,
  useResultColumns,
} from "@/_components/_display/resultsTable/resultColumns";
import WatchYourGamesButton from "@/_components/_actions/WatchYourGamesButton";
import WatchGamesModal from "@/_pages/UserMatchRequests/UserMatchRequests/_modals/WatchGamesModal";
import useStateWithLocalStorage from "@/_components/_hooks/useStateWithLocalStorage";

interface ResultsTableProps {
  data: ResultsTable_node$key;
}

export default function ResultsTable(props: ResultsTableProps) {
  const [columnVisibility, setColumnVisibility] =
    useStateWithLocalStorage<VisibilityState>(
      "Results_ResultsTable_ColumnVisibility",
      {},
    );

  const { data, loadNext, hasNext } = usePaginationFragment(
    graphql`
      fragment ResultsTable_node on Query
      @refetchable(queryName: "ResultsTablePaginationQuery")
      @argumentDefinitions(
        cursor: { type: "String" }
        first: { type: "Int", defaultValue: 50 }
      ) {
        results(first: $first, after: $cursor)
          @connection(key: "ResultsTable_node_results") {
          edges {
            node {
              ...resultColumns_result
            }
          }
        }
      }
    `,
    props.data,
  );
  const [isWatchGamesModalOpen, setIsWatchGamesModalOpen] = useState(false);

  const [isPending] = useTransition();
  const matchData = useMemo(
    () => getNodes(data?.results).map(readResultRow),
    [data],
  );

  const columns = useResultColumns();

  const { loadMoreRef } = useInfiniteScroll(() => loadNext(50), hasNext);

  const table = useReactTable({
    data: matchData,
    columns,
    getCoreRowModel: getCoreRowModel(),
    enableColumnResizing: true,
    columnResizeMode: "onChange",
    manualSorting: true,
    initialState: {
      columnVisibility: columnVisibility ?? undefined,
    },
    state: {
      columnVisibility: columnVisibility ?? {},
    },

    onColumnVisibilityChange: (updater) => {
      const next =
        typeof updater === "function"
          ? updater(columnVisibility ?? {})
          : updater;
      setColumnVisibility(next);
    },
  });

  const hasItems = matchData.length > 0;

  return (
    <div>
      <Suspense fallback={<LoadingDots />}>
        {hasItems ? (
          <TableContainer
            table={table}
            loading={isPending}
            appendHeader={
              <WatchYourGamesButton
                onClick={() => setIsWatchGamesModalOpen(true)}
              >
                <span>Watch Replays on Twitch</span>
              </WatchYourGamesButton>
            }
          />
        ) : (
          <NoItemsInListMessage>
            <p>No Results meet the criteria...</p>
          </NoItemsInListMessage>
        )}
      </Suspense>

      {hasNext ? (
        <div className="flex justify-center mt-6" ref={loadMoreRef}>
          <LoadingMoreItems loadingMessage="Loading more results..." />
        </div>
      ) : !hasNext && hasItems ? (
        <div className="mt-8">
          <NoMoreItems />
        </div>
      ) : null}
      <WatchGamesModal
        isOpen={isWatchGamesModalOpen}
        onClose={() => setIsWatchGamesModalOpen(false)}
      />
    </div>
  );
}
