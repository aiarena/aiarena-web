import { graphql, useFragment } from "react-relay";
import {
  createColumnHelper,
  getCoreRowModel,
  useReactTable,
} from "@tanstack/react-table";
import { useMemo } from "react";
import { TableContainer } from "@/_components/_actions/TableContainer";
import { MatchupStatsTable_node$key } from "./__generated__/MatchupStatsTable_node.graphql";
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

  const matchupStats = getNodes(data.competitionMatchupStats);
  const columnHelper = createColumnHelper<(typeof matchupStats)[number]>();

  const columns = useMemo(
    () => [
      columnHelper.accessor((row) => row.opponent.bot.name, {
        id: "opponent",
        header: "Opponent",
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
        cell: (info) => (
          <span className="font-mono">{info.getValue() || "N/A"}</span>
        ),
        meta: { priority: 1 },
      }),
      columnHelper.accessor((row) => row.matchCount, {
        id: "matches",
        header: "Matches",
        cell: (info) => <span className="font-mono">{info.getValue()}</span>,
        meta: { priority: 1 },
      }),
      columnHelper.accessor((row) => row.winCount, {
        id: "win",
        header: "Win",
        cell: (info) => <span className="font-mono">{info.getValue()}</span>,
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
        cell: (info) => <span className="font-mono">{info.getValue()}</span>,
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
        cell: (info) => <span className="font-mono">{info.getValue()}</span>,
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
        cell: (info) => <span className="font-mono">{info.getValue()}</span>,
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
    data: matchupStats,
    columns,
    getCoreRowModel: getCoreRowModel(),
  });

  return (
    <div>
      <div className="divider mb-6">
        <span></span>
        <span>
          <h2 className="text-xl font-semibold">Matchups</h2>
        </span>
        <span></span>
      </div>
      <TableContainer table={table} loading={false} />
    </div>
  );
}
