import { graphql, usePaginationFragment } from "react-relay";
import {
  createColumnHelper,
  getCoreRowModel,
  SortingState,
  useReactTable,
} from "@tanstack/react-table";
import { startTransition, useEffect, useMemo, useState } from "react";
import { TableContainer } from "@/_components/_actions/TableContainer";
import {
  MapStatsTable_node$data,
  MapStatsTable_node$key,
} from "./__generated__/MapStatsTable_node.graphql";
import { getNodes } from "@/_lib/relayHelpers.ts";
import { parseSort } from "@/_lib/tanstack_utils";
import NoItemsInListMessage from "@/_components/_display/NoItemsInListMessage";
import LoadingMoreItems from "@/_components/_display/LoadingMoreItems";
import NoMoreItems from "@/_components/_display/NoMoreItems";
import { useInfiniteScroll } from "@/_components/_hooks/useInfiniteScroll";

interface MapStatsTableProps {
  data: MapStatsTable_node$key;
}

export default function MapStatsTable(props: MapStatsTableProps) {
  const { data, loadNext, hasNext, refetch } = usePaginationFragment(
    graphql`
      fragment MapStatsTable_node on CompetitionParticipationType
      @argumentDefinitions(
        cursor: { type: "String" }
        first: { type: "Int", defaultValue: 50 }
        orderBy: { type: "String" }
      )
      @refetchable(queryName: "MapStatsTablePaginationQuery") {
        competitionMapStats(first: $first, after: $cursor, orderBy: $orderBy)
          @connection(key: "CompetitionParticipation__competitionMapStats") {
          __id
          edges {
            node {
              map {
                name
              }
              matchCount
              winCount
              winPerc
              lossCount
              lossPerc
              tieCount
              tiePerc
              crashCount
              crashPerc
            }
          }
        }
      }
    `,
    props.data
  );

  type MapStatsType = NonNullable<
    NonNullable<
      NonNullable<
        MapStatsTable_node$data["competitionMapStats"]
      >["edges"][number]
    >["node"]
  >;

  const mapStatsData = useMemo(
    () => getNodes<MapStatsType>(data?.competitionMapStats),
    [data]
  );

  const columnHelper = createColumnHelper<MapStatsType>();

  const columns = useMemo(
    () => [
      columnHelper.accessor((row) => row.map.name, {
        id: "map",
        header: "Map",
        cell: (info) => info.getValue(),
        meta: { priority: 1 },
        size: 250,
      }),
      columnHelper.accessor((row) => row.matchCount, {
        id: "matches",
        header: "Matches",
        cell: (info) => info.getValue(),
        meta: { priority: 1 },
        size: 95,
      }),
      columnHelper.accessor((row) => row.winCount, {
        id: "win",
        header: "Wins",
        cell: (info) => info.getValue(),
        meta: { priority: 1 },
        size: 95,
      }),
      columnHelper.accessor((row) => row.winPerc, {
        id: "winPerc",
        header: "Win %",
        cell: (info) => {
          return `${info.getValue().toFixed(1)} %`;
        },
        meta: { priority: 1 },
        size: 95,
      }),
      columnHelper.accessor((row) => row.lossCount, {
        id: "loss",
        header: "Losses",
        cell: (info) => info.getValue(),
        meta: { priority: 1 },
        size: 95,
      }),
      columnHelper.accessor((row) => row.lossPerc, {
        id: "lossPerc",
        header: "Loss %",
        cell: (info) => {
          return `${info.getValue().toFixed(1)} %`;
        },
        meta: { priority: 1 },
        size: 95,
      }),
      columnHelper.accessor((row) => row.tieCount, {
        id: "tie",
        header: "Ties",
        cell: (info) => info.getValue(),
        meta: { priority: 1 },
        size: 95,
      }),
      columnHelper.accessor((row) => row.tiePerc, {
        id: "tiePerc",
        header: "Tie %",
        cell: (info) => {
          return `${info.getValue().toFixed(1)} %`;
        },
        meta: { priority: 1 },
        size: 95,
      }),
      columnHelper.accessor((row) => row.crashCount, {
        id: "crash",
        header: "Crashes",
        cell: (info) => info.getValue(),
        meta: { priority: 1 },
        size: 95,
      }),
      columnHelper.accessor((row) => row.crashPerc, {
        id: "crashPerc",
        header: "Crash %",
        cell: (info) => {
          return `${info.getValue().toFixed(1)} %`;
        },
        meta: { priority: 1 },
        size: 95,
      }),
    ],
    [columnHelper]
  );

  const { loadMoreRef } = useInfiniteScroll(() => loadNext(50), hasNext);
  const [sorting, setSorting] = useState<SortingState>([]);

  useEffect(() => {
    const sortingMap: Record<string, string> = {
      map: "map__name",
      matches: "match_count",
      win: "win_count",
      winPerc: "win_perc",
      loss: "loss_count",
      lossPerc: "loss_perc",
      tie: "tie_count",

      tiePerc: "tie_perc",
      crash: "crash_count",
      crashPerc: "crash_perc",
    };
    startTransition(() => {
      const sortString = parseSort(sortingMap, sorting);
      refetch({ orderBy: sortString });
    });
  }, [sorting, refetch]);

  const table = useReactTable({
    data: mapStatsData,
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
  const hasItems = mapStatsData.length > 0;
  return (
    <div>
      {hasItems ? (
        <TableContainer table={table} loading={false} />
      ) : (
        <NoItemsInListMessage>
          <p>No map stats available yet...</p>
        </NoItemsInListMessage>
      )}
      {hasNext ? (
        <div className="flex justify-center mt-6" ref={loadMoreRef}>
          <LoadingMoreItems loadingMessage="Loading more maps..." />
        </div>
      ) : !hasNext && hasItems ? (
        <div className="mt-8">
          <NoMoreItems />
        </div>
      ) : null}
    </div>
  );
}
