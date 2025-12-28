import { graphql, useFragment } from "react-relay";
import {
  createColumnHelper,
  getCoreRowModel,
  useReactTable,
} from "@tanstack/react-table";
import { useMemo } from "react";
import { TableContainer } from "@/_components/_actions/TableContainer";
import {
  MatchupStatsTable_node$data,
  MatchupStatsTable_node$key,
} from "./__generated__/MatchupStatsTable_node.graphql";
import { withAtag } from "@/_lib/tanstack_utils";
import { getIDFromBase64, getNodes } from "@/_lib/relayHelpers";

interface MatchupStatsTableProps {
  data: MatchupStatsTable_node$key;
}

export default function MatchupStatsTable(props: MatchupStatsTableProps) {
  const data = useFragment(
    graphql`
      fragment MatchupStatsTable_node on CompetitionParticipationType {
        competitionMatchupStats {
          edges {
            node {
              opponent {
                id
                bot {
                  id
                  name
                  playsRace {
                    name
                    label
                    id
                  }
                }
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

  type MatchupStatsType = NonNullable<
    NonNullable<
      NonNullable<
        MatchupStatsTable_node$data["competitionMatchupStats"]
      >["edges"][number]
    >["node"]
  >;

  const matchupStatsData = useMemo(
    () => getNodes<MatchupStatsType>(data?.competitionMatchupStats),
    [data]
  );

  const columnHelper = createColumnHelper<MatchupStatsType>();

  const columns = useMemo(
    () => [
      columnHelper.accessor((row) => row.opponent.bot.name, {
        id: "opponent",
        header: "Opponent",
        enableSorting: false,
        cell: (info) =>
          withAtag(
            info.getValue(),
            `/bots/${getIDFromBase64(info.row.original.opponent.bot.id, "BotType")}`,
            `View bot profile for ${info.getValue()}`
          ),
        meta: { priority: 1 },
      }),
      columnHelper.accessor((row) => row.opponent.bot.playsRace.name ?? "", {
        id: "race",
        header: "Race",
        enableSorting: false,
        cell: (info) => info.getValue() || "N/A",
        meta: { priority: 1 },
        size: 95,
      }),
      columnHelper.accessor((row) => row.matchCount, {
        id: "matches",
        header: "Matches",
        enableSorting: false,

        cell: (info) => info.getValue(),
        meta: { priority: 1 },
        size: 95,
      }),
      columnHelper.accessor((row) => row.winCount, {
        id: "win",
        header: "Wins",
        enableSorting: false,
        cell: (info) => info.getValue(),
        meta: { priority: 1 },
        size: 95,
      }),
      columnHelper.accessor((row) => row.winPerc, {
        id: "winPerc",
        header: "Win %",
        enableSorting: false,
        cell: (info) => {
          return `${info.getValue().toFixed(1)} %`;
        },
        meta: { priority: 1 },
        size: 95,
      }),
      columnHelper.accessor((row) => row.lossCount, {
        id: "loss",
        header: "Losses",
        enableSorting: false,
        cell: (info) => info.getValue(),
        meta: { priority: 1 },
        size: 95,
      }),
      columnHelper.accessor((row) => row.lossPerc, {
        id: "lossPerc",
        header: "Loss %",
        enableSorting: false,
        cell: (info) => {
          return `${info.getValue().toFixed(1)} %`;
        },
        meta: { priority: 1 },
        size: 95,
      }),
      columnHelper.accessor((row) => row.tieCount, {
        id: "tie",
        header: "Ties",
        enableSorting: false,
        cell: (info) => info.getValue(),
        meta: { priority: 1 },
        size: 95,
      }),
      columnHelper.accessor((row) => row.tiePerc, {
        id: "tiePerc",
        header: "Tie %",
        enableSorting: false,

        cell: (info) => {
          return `${info.getValue().toFixed(1)} %`;
        },
        meta: { priority: 1 },
      }),
      columnHelper.accessor((row) => row.crashCount, {
        id: "crash",
        header: "Crashes",
        enableSorting: false,

        cell: (info) => info.getValue(),
        meta: { priority: 1 },
        size: 95,
      }),
      columnHelper.accessor((row) => row.crashPerc, {
        id: "crashPerc",
        header: "Crash %",
        enableSorting: false,
        cell: (info) => {
          return `${info.getValue().toFixed(1)} %`;
        },
        meta: { priority: 1 },
        size: 95,
      }),
    ],
    [columnHelper]
  );

  const table = useReactTable({
    data: matchupStatsData,
    columns,
    getCoreRowModel: getCoreRowModel(),
    enableColumnResizing: true,
    columnResizeMode: "onChange",
    manualSorting: true,
  });

  return (
    <div>
      <div className="divider mb-6">
        <h2 className="text-xl font-semibold">Matchups</h2>
      </div>
      <TableContainer table={table} loading={false} />
    </div>
  );
}
