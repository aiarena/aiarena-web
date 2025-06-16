import { graphql, usePaginationFragment } from "react-relay";
import {
  createColumnHelper,
  getCoreRowModel,
  SortingState,
  useReactTable,
} from "@tanstack/react-table";
import {
  MatchRequestsTable_viewer$data,
  MatchRequestsTable_viewer$key,
} from "./__generated__/MatchRequestsTable_viewer.graphql";
import { getIDFromBase64, getNodes } from "@/_lib/relayHelpers";

import LoadingDots from "../_display/LoadingDots";
import { useInfiniteScroll } from "../_hooks/useInfiniteScroll";
import { Suspense, useEffect, useMemo, useState } from "react";
import { getDateTimeISOString } from "@/_lib/dateUtils";

import { getMatchResultParsed } from "@/_lib/parseMatchResult";
import { TableContainer } from "./TableContainer";
import { parseSort, withAtag } from "@/_lib/tanstack_utils";
import LoadingMoreItems from "../_display/LoadingMoreItems";
import NoMoreItems from "../_display/NoMoreItems";

interface MatchRequestsTableProps {
  viewer: MatchRequestsTable_viewer$key;
  loading: boolean;
}

export default function MatchRequestsTable(props: MatchRequestsTableProps) {
  const {
    data: matchData,
    loadNext,
    hasNext,
    refetch,
  } = usePaginationFragment(
    graphql`
      fragment MatchRequestsTable_viewer on Viewer
      @argumentDefinitions(
        cursor: { type: "String" }
        first: { type: "Int", defaultValue: 50 }
        orderBy: { type: "String" }
      )
      @refetchable(queryName: "MatchRequestsTablePaginationQuery") {
        requestedMatches(first: $first, after: $cursor, orderBy: $orderBy)
          @connection(key: "UserMatchRequestsSection_viewer_requestedMatches") {
          edges {
            node {
              id
              started
              participant1 {
                id
                name
              }
              participant2 {
                id
                name
              }
              result {
                type
                winner {
                  name
                }
              }
              tags
              map {
                name
              }
            }
          }
        }
      }
    `,
    props.viewer
  );

  type MatchType = NonNullable<
    NonNullable<
      NonNullable<
        MatchRequestsTable_viewer$data["requestedMatches"]
      >["edges"][number]
    >["node"]
  >;

  const data = useMemo(
    () => getNodes<MatchType>(matchData?.requestedMatches),
    [matchData]
  );

  const columnHelper = createColumnHelper<MatchType>();

  const columns = useMemo(
    () => [
      columnHelper.accessor((row) => row.id, {
        id: "id",
        header: "ID",
        cell: (info) =>
          withAtag(
            getIDFromBase64(info.getValue(), "MatchType") || "",
            `/matches/${getIDFromBase64(info.getValue(), "MatchType")}`,
            `View match details for match ID ${info.getValue()}`
          ),

        meta: { priority: 1 },
      }),
      columnHelper.accessor((row) => row.participant1?.name || "", {
        id: "participant1",
        header: "Agent 1",
        cell: (info) =>
          withAtag(
            info.getValue() || "",
            `/bots/${getIDFromBase64(info.row.original.participant1?.id, "BotType")}`,
            `View bot profile for ${info.getValue()}, Agent 1`
          ),
        meta: { priority: 1 },
      }),
      columnHelper.accessor((row) => row.participant2?.name || "", {
        id: "participant2",
        header: "Agent 2",
        cell: (info) =>
          withAtag(
            info.getValue() || "",
            `/bots/${getIDFromBase64(info.row.original.participant2?.id, "BotType")}`,
            `View bot profile for ${info.getValue()}, Agent 2`
          ),
        meta: { priority: 1 },
      }),
      columnHelper.accessor((row) => row.map?.name ?? "", {
        id: "map",
        header: "Map",
        cell: (info) => info.getValue(),
        meta: { priority: 1 },
      }),
      columnHelper.accessor((row) => row.tags?.join(", ") ?? "", {
        id: "tags",
        header: "Tags",
        cell: (info) => info.getValue(),
        meta: { priority: 1 },
      }),
      columnHelper.accessor((row) => row.started ?? "A", {
        id: "started",
        header: "Started",
        cell: (info) => {
          const getTime = getDateTimeISOString(info.getValue());
          return getTime !== "" ? getTime : "In Queue";
        },
        meta: { priority: 1 },
      }),

      columnHelper.accessor((row) => row.result?.type || "A", {
        id: "result",
        header: "Result",
        cell: (info) => {
          const getResult = getMatchResultParsed(
            info.getValue(),
            info.row.original.participant1?.name,
            info.row.original.participant2?.name
          );
          return getResult != "" ? getResult : "In Queue";
        },

        meta: { priority: 1 },
      }),
    ],
    [columnHelper]
  );

  const { loadMoreRef } = useInfiniteScroll(() => loadNext(50), hasNext);
  const [sorting, setSorting] = useState<SortingState>([]);

  useEffect(() => {
    const sortingMap: Record<string, string> = {
      id: "id",
      participant1: "participant1__bot__name",
      participant2: "participant2__bot__name",
      result: "result__type",
      map: "map__name",
      started: "started",
      tags: "tags",
    };

    const sortString = parseSort(sortingMap, sorting);
    refetch({ orderBy: sortString });
  }, [sorting, refetch]);

  const table = useReactTable({
    data,
    columns,
    getCoreRowModel: getCoreRowModel(),
    enableColumnResizing: true,
    columnResizeMode: "onChange",
    manualSorting: true,

    state: {
      sorting,
    },

    onSortingChange: setSorting,
  });

  return (
    <div>
      <Suspense fallback={<LoadingDots />}>
        <TableContainer table={table} loading={props.loading} />
      </Suspense>
      {hasNext ? (
        <div className="flex justify-center mt-6" ref={loadMoreRef}>
          <LoadingMoreItems loadingMessage="Loading more Match Requests..." />
        </div>
      ) : (
        <div className="mt-8">
          <NoMoreItems />
        </div>
      )}
    </div>
  );
}
