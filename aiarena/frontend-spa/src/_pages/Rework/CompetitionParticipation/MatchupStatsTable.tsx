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
  MatchupStatsTable_node$data,
  MatchupStatsTable_node$key,
} from "./__generated__/MatchupStatsTable_node.graphql";
import { parseSort, withAtag } from "@/_lib/tanstack_utils";
import { getIDFromBase64, getNodes } from "@/_lib/relayHelpers";
import { useInfiniteScroll } from "@/_components/_hooks/useInfiniteScroll";
import NoItemsInListMessage from "@/_components/_display/NoItemsInListMessage";
import LoadingMoreItems from "@/_components/_display/LoadingMoreItems";
import NoMoreItems from "@/_components/_display/NoMoreItems";
import { RenderRace } from "@/_components/_display/RenderRace";

interface MatchupStatsTableProps {
  data: MatchupStatsTable_node$key;
}

export default function MatchupStatsTable(props: MatchupStatsTableProps) {
  const { data, loadNext, hasNext, refetch } = usePaginationFragment(
    graphql`
      fragment MatchupStatsTable_node on CompetitionParticipationType
      @argumentDefinitions(
        cursor: { type: "String" }
        first: { type: "Int", defaultValue: 50 }
        orderBy: { type: "String" }
      )
      @refetchable(queryName: "MatchupStatsTablePaginationQuery") {
        competitionMatchupStats(
          first: $first
          after: $cursor
          orderBy: $orderBy
        )
          @connection(
            key: "CompetitionParticipation__competitionMatchupStats"
          ) {
          __id
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
        cell: (info) => {
          return <RenderRace race={info.row.original.opponent.bot.playsRace} />;
        },
        meta: { priority: 1 },
        size: 95,
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
      opponent: "opponent__bot__name",
      race: "opponent__bot__plays_race__label",
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
    data: matchupStatsData,
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
  const hasItems = matchupStatsData.length > 0;
  return (
    <div>
      {hasItems ? (
        <TableContainer table={table} loading={false} />
      ) : (
        <NoItemsInListMessage>
          <p>No matchup stats available...</p>
        </NoItemsInListMessage>
      )}
      {hasNext ? (
        <div className="flex justify-center mt-6" ref={loadMoreRef}>
          <LoadingMoreItems loadingMessage="Loading more opponents..." />
        </div>
      ) : !hasNext && hasItems ? (
        <div className="mt-8">
          <NoMoreItems />
        </div>
      ) : null}
    </div>
  );
}
