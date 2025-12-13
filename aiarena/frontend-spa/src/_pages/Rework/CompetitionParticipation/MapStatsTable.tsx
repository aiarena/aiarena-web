import { graphql, useFragment } from "react-relay";
import {
  createColumnHelper,
  getCoreRowModel,
  useReactTable,
} from "@tanstack/react-table";
import { useMemo } from "react";
import { TableContainer } from "@/_components/_actions/TableContainer";
import {
  MapStatsTable_node$data,
  MapStatsTable_node$key,
} from "./__generated__/MapStatsTable_node.graphql";
import { getNodes } from "@/_lib/relayHelpers.ts";

interface MapStatsTableProps {
  data: MapStatsTable_node$key;
}

export default function MapStatsTable(props: MapStatsTableProps) {
  const data = useFragment(
    graphql`
      fragment MapStatsTable_node on CompetitionParticipationType {
        competitionMapStats {
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
        enableSorting: false,
        cell: (info) => info.getValue(),
        meta: { priority: 1 },
      }),
      columnHelper.accessor((row) => row.matchCount, {
        id: "matches",
        header: "Matches",
        enableSorting: false,
        cell: (info) => info.getValue(),
        meta: { priority: 1 },
      }),
      columnHelper.accessor((row) => row.winCount, {
        id: "win",
        header: "Win",
        enableSorting: false,
        cell: (info) => info.getValue(),
        meta: { priority: 1 },
      }),
      columnHelper.accessor((row) => row.winPerc, {
        id: "winPerc",
        header: "%",
        enableSorting: false,
        cell: (info) => {
          info.getValue().toFixed(2);
        },
        meta: { priority: 1 },
      }),
      columnHelper.accessor((row) => row.lossCount, {
        id: "loss",
        header: "Loss",
        enableSorting: false,
        cell: (info) => info.getValue(),
        meta: { priority: 1 },
      }),
      columnHelper.accessor((row) => row.lossPerc, {
        id: "lossPerc",
        header: "%",
        enableSorting: false,
        cell: (info) => info.getValue().toFixed(2),
        meta: { priority: 1 },
      }),
      columnHelper.accessor((row) => row.tieCount, {
        id: "tie",
        header: "Tie",
        enableSorting: false,
        cell: (info) => info.getValue(),
        meta: { priority: 1 },
      }),
      columnHelper.accessor((row) => row.tiePerc, {
        id: "tiePerc",
        header: "%",
        enableSorting: false,
        cell: (info) => info.getValue().toFixed(2),
        meta: { priority: 1 },
      }),
      columnHelper.accessor((row) => row.crashCount, {
        id: "crash",
        header: "Crash",
        enableSorting: false,
        cell: (info) => info.getValue(),
        meta: { priority: 1 },
      }),
      columnHelper.accessor((row) => row.crashPerc, {
        id: "crashPerc",
        header: "%",
        enableSorting: false,

        cell: (info) => info.getValue().toFixed(2),
        meta: { priority: 1 },
      }),
    ],
    [columnHelper]
  );

  const table = useReactTable({
    data: mapStatsData,
    columns,
    getCoreRowModel: getCoreRowModel(),
    enableColumnResizing: true,
    columnResizeMode: "onChange",
    manualSorting: true,
  });

  return (
    <div>
      <div className="divider mb-6">
        <h2 className="text-xl font-semibold">Maps</h2>
      </div>
      <TableContainer table={table} loading={false} />
    </div>
  );
}
