import { graphql, useFragment } from "react-relay";
import {
  createColumnHelper,
  getCoreRowModel,
  useReactTable,
} from "@tanstack/react-table";
import { useMemo } from "react";
import { TableContainer } from "@/_components/_actions/TableContainer";
import { MapStatsTable_node$key } from "./__generated__/MapStatsTable_node.graphql";
import {getNodes} from "@/_lib/relayHelpers.ts";

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

  const mapStats = getNodes(data.competitionMapStats);
  const columnHelper = createColumnHelper<typeof mapStats[number]>();

  const columns = useMemo(
    () => [
      columnHelper.accessor((row) => row.map.name, {
        id: "map",
        header: "Map",
        cell: (info) => (
          <span className="font-mono">{info.getValue()}</span>
        ),
        meta: { priority: 1 },
      }),
      columnHelper.accessor((row) => row.matchCount, {
        id: "matches",
        header: "Matches",
        cell: (info) => (
          <span className="font-mono">{info.getValue()}</span>
        ),
        meta: { priority: 1 },
      }),
      columnHelper.accessor((row) => row.winCount, {
        id: "win",
        header: "Win",
        cell: (info) => (
          <span className="font-mono">{info.getValue()}</span>
        ),
        meta: { priority: 1 },
      }),
      columnHelper.accessor((row) => row.winPerc, {
        id: "winPerc",
        header: "%",
        cell: (info) => (
          <span className="font-mono">{info.getValue().toFixed(2)}</span>
        ),
        meta: { priority: 1 },
      }),
      columnHelper.accessor((row) => row.lossCount, {
        id: "loss",
        header: "Loss",
        cell: (info) => (
          <span className="font-mono">{info.getValue()}</span>
        ),
        meta: { priority: 1 },
      }),
      columnHelper.accessor((row) => row.lossPerc, {
        id: "lossPerc",
        header: "%",
        cell: (info) => (
          <span className="font-mono">{info.getValue().toFixed(2)}</span>
        ),
        meta: { priority: 1 },
      }),
      columnHelper.accessor((row) => row.tieCount, {
        id: "tie",
        header: "Tie",
        cell: (info) => (
          <span className="font-mono">{info.getValue()}</span>
        ),
        meta: { priority: 1 },
      }),
      columnHelper.accessor((row) => row.tiePerc, {
        id: "tiePerc",
        header: "%",
        cell: (info) => (
          <span className="font-mono">{info.getValue().toFixed(2)}</span>
        ),
        meta: { priority: 1 },
      }),
      columnHelper.accessor((row) => row.crashCount, {
        id: "crash",
        header: "Crash",
        cell: (info) => (
          <span className="font-mono">{info.getValue()}</span>
        ),
        meta: { priority: 1 },
      }),
      columnHelper.accessor((row) => row.crashPerc, {
        id: "crashPerc",
        header: "%",
        cell: (info) => (
          <span className="font-mono">{info.getValue().toFixed(2)}</span>
        ),
        meta: { priority: 1 },
      }),
    ],
    [columnHelper]
  );

  const table = useReactTable({
    data: mapStats,
    columns,
    getCoreRowModel: getCoreRowModel(),
  });

  return (
    <div>
      <div className="divider mb-6">
        <span></span>
        <span>
          <h2 className="text-xl font-semibold">Maps</h2>
        </span>
        <span></span>
      </div>
      <TableContainer table={table} loading={false} />
    </div>
  );
}
