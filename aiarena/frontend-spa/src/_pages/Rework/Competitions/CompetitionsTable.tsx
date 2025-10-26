import { graphql, usePaginationFragment } from "react-relay";
import {
  createColumnHelper,
  getCoreRowModel,
  useReactTable,
} from "@tanstack/react-table";

import { getIDFromBase64, getNodes } from "@/_lib/relayHelpers";

import { Suspense, useMemo, useState, useTransition } from "react";
import { getDateTimeISOString } from "@/_lib/dateUtils";

import { withAtag } from "@/_lib/tanstack_utils";

import NoMoreItems from "@/_components/_display/NoMoreItems";
import LoadingMoreItems from "@/_components/_display/LoadingMoreItems";
import { TableContainer } from "@/_components/_actions/TableContainer";
import LoadingDots from "@/_components/_display/LoadingDots";
import { useInfiniteScroll } from "@/_components/_hooks/useInfiniteScroll";

import WatchGamesModal from "@/_pages/UserMatchRequests/UserMatchRequests/_modals/WatchGamesModal";
import {
  CompetitionsTable$data,
  CompetitionsTable$key,
} from "./__generated__/CompetitionsTable.graphql";

interface CompetitionsTableProps {
  data: CompetitionsTable$key;
}

export default function CompetitionsTable(props: CompetitionsTableProps) {
  const { data, loadNext, hasNext } = usePaginationFragment(
    graphql`
      fragment CompetitionsTable on Query
      @refetchable(queryName: "CompetitionsTablePaginationQuery")
      @argumentDefinitions(
        cursor: { type: "String" }
        first: { type: "Int", defaultValue: 50 }
        status: { type: "CoreCompetitionStatusChoices", defaultValue: CLOSED }
      ) {
        closedCompetitions: competitions(
          first: $first
          after: $cursor
          status: $status
        ) @connection(key: "CompetitionsTable__closedCompetitions") {
          edges {
            node {
              id
              name
              status
              url
              dateCreated
              dateOpened
              dateClosed
            }
          }
        }
      }
    `,
    props.data
  );

  type CompetitionType = NonNullable<
    NonNullable<
      NonNullable<CompetitionsTable$data["closedCompetitions"]>["edges"][number]
    >["node"]
  >;
  const [isWatchGamesModalOpen, setIsWatchGamesModalOpen] = useState(false);

  const [isPending] = useTransition();
  const matchData = useMemo(
    () => getNodes<CompetitionType>(data?.closedCompetitions),
    [data]
  );

  const columnHelper = createColumnHelper<CompetitionType>();

  const columns = useMemo(
    () => [
      columnHelper.accessor((row) => row.id, {
        id: "id",
        header: "ID",
        enableSorting: false,
        cell: (info) =>
          withAtag(
            getIDFromBase64(info.getValue(), "CompetitionType") || "",
            `/competitions/${getIDFromBase64(info.getValue(), "CompetitionType")}`,
            `View competition details for Competition ID ${getIDFromBase64(info.getValue(), "CompetitionType")}}`
          ),

        meta: { priority: 1 },
      }),
      columnHelper.accessor((row) => row.name || "", {
        id: "name",
        header: "Name",
        enableSorting: false,
        cell: (info) => {
          const name = info.row.original.name;

          return withAtag(
            name || "",
            `/competitions/${getIDFromBase64(info.getValue(), "CompetitionType")}`,
            `View competition details for Competition ${name}`
          );
        },
        meta: { priority: 1 },
      }),

      columnHelper.accessor((row) => row.status || "", {
        id: "status",
        header: "Status",
        enableSorting: false,
        cell: (info) => {
          const status = info.row.original.status;

          return status;
        },

        meta: { priority: 1 },
      }),

      columnHelper.accessor((row) => row.dateCreated ?? "", {
        id: "dateCreated",
        header: "Created",
        enableSorting: false,
        cell: (info) => {
          const getTime = getDateTimeISOString(info.getValue());
          return getTime;
        },
        meta: { priority: 1 },
      }),
      columnHelper.accessor((row) => row.dateClosed ?? "", {
        id: "dateClosed",
        header: "Closed",
        enableSorting: false,
        cell: (info) => {
          const getTime = getDateTimeISOString(info.getValue());
          return getTime !== "" ? getTime : "";
        },
        meta: { priority: 1 },
      }),
    ],
    [columnHelper]
  );

  const { loadMoreRef } = useInfiniteScroll(() => loadNext(50), hasNext);

  const table = useReactTable({
    data: matchData,
    columns,
    getCoreRowModel: getCoreRowModel(),
    enableColumnResizing: true,
    columnResizeMode: "onChange",
    manualSorting: true,
  });

  const hasItems = matchData.length > 0;

  return (
    <div>
      <Suspense fallback={<LoadingDots />}>
        <TableContainer table={table} loading={isPending} minHeight={40} />
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
