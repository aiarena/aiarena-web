import { graphql, usePaginationFragment } from "react-relay";
import { getIDFromBase64, getNodes } from "@/_lib/relayHelpers";
import { Suspense, useMemo, useState } from "react";
import {
  createColumnHelper,
  getCoreRowModel,
  SortingState,
  useReactTable,
} from "@tanstack/react-table";
import { withAtag } from "@/_lib/tanstack_utils";
import { useInfiniteScroll } from "@/_components/_hooks/useInfiniteScroll";
import LoadingDots from "@/_components/_display/LoadingDots";
import { TableContainer } from "@/_components/_actions/TableContainer";
import LoadingMoreItems from "@/_components/_display/LoadingMoreItems";
import NoMoreItems from "@/_components/_display/NoMoreItems";
import {
  RankingsSection_competition$data,
  RankingsSection_competition$key,
} from "./__generated__/RankingsSection_competition.graphql";
import EloTrendIcon from "@/_components/_display/EloTrendIcon";
import BotIcon from "@/_components/_display/BotIcon";
import RenderCodeLanguage from "@/_components/_display/RenderCodeLanguage";

interface RankingsSectionProps {
  competition: RankingsSection_competition$key;
}

type ParticipationType = NonNullable<
  NonNullable<
    NonNullable<
      RankingsSection_competition$data["participants"]
    >["edges"][number]
  >["node"]
>;

type ParticipantRow = ParticipationType & {
  __kind: "participant";
  rank: number;
};

type DivisionHeaderRow = {
  __kind: "divisionHeader";
  divisionNum: ParticipationType["divisionNum"];
  id: string;
};

export type RankingsRow = ParticipantRow | DivisionHeaderRow;

export default function RankingsSection({ competition }: RankingsSectionProps) {
  const { data, loadNext, hasNext } = usePaginationFragment(
    graphql`
      fragment RankingsSection_competition on CompetitionType
      @refetchable(queryName: "CompetitionRankingsPaginationQuery")
      @argumentDefinitions(
        cursor: { type: "String" }
        first: { type: "Int", defaultValue: 50 }
      ) {
        participants(first: $first, after: $cursor)
          @connection(key: "RankingsSection_competition_participants") {
          edges {
            node {
              divisionNum
              bot {
                id
                name
                playsRace {
                  name
                  label
                  id
                }
                user {
                  id
                  username
                  ...BotIcon_user
                }
                type
              }
              elo
              winPerc
              trend
              id
            }
          }
        }
      }
    `,
    competition
  );

  const rankingsData = useMemo(
    () => getNodes<ParticipationType>(data?.participants),
    [data]
  );

  const tableData: RankingsRow[] = useMemo(() => {
    if (!rankingsData) return [];

    const result: RankingsRow[] = [];
    let lastDivision: number | null = null;
    let rank = 0;

    for (const row of rankingsData) {
      const division = row.divisionNum ?? null;

      if (division !== lastDivision) {
        result.push({
          __kind: "divisionHeader",
          divisionNum: division,
          id: `division-header-${division ?? "none"}`,
        });
        lastDivision = division;
      }

      rank += 1;
      result.push({
        ...row,
        __kind: "participant",
        rank,
      });
    }

    return result;
  }, [rankingsData]);

  const columnHelper = createColumnHelper<RankingsRow>();
  const columns = useMemo(
    () => [
      columnHelper.display({
        id: "index",
        header: "Rank",
        enableSorting: false,
        cell: ({ row }) => {
          const original = row.original;
          if (original.__kind !== "participant") return null;
          return original.rank;
        },
        meta: { priority: 1 },
        size: 5,
      }),

      columnHelper.display({
        id: "name",
        header: "Name",
        enableSorting: false,
        cell: (info) => {
          const original = info.row.original;
          if (original.__kind !== "participant") return null;

          const bot = original.bot;
          return withAtag(
            bot.name ?? "",
            `/bots/${getIDFromBase64(bot.id, "BotType")}`,
            `View bot profile for ${bot.name}`
          );
        },
        meta: { priority: 1 },
      }),

      columnHelper.display({
        id: "elo",
        header: "ELO",
        enableSorting: false,
        cell: (info) => {
          const original = info.row.original;
          if (original.__kind !== "participant") return null;

          const elo = original.elo ?? "";
          const eloChange = original.trend;
          return (
            <span
              className="flex items-center gap-1"
              title={`ELO changed ${eloChange} in the last 30 games`}
            >
              {elo}
              <EloTrendIcon trend={eloChange} />
            </span>
          );
        },
        meta: { priority: 1 },
        size: 100,
      }),

      columnHelper.display({
        id: "playsRace",
        header: "Race",
        enableSorting: false,
        cell: ({ row }) => {
          const original = row.original;
          if (original.__kind !== "participant") return null;
          return original.bot.playsRace.name ?? "--";
        },
        meta: { priority: 4 },
      }),

      columnHelper.display({
        id: "type",
        header: "Type",
        enableSorting: false,
        cell: ({ row }) => {
          const original = row.original;
          if (original.__kind !== "participant") return null;
          return <RenderCodeLanguage type={`${original.bot.type ?? "--"}`} />;
        },
        meta: { priority: 4 },
      }),

      columnHelper.display({
        id: "username",
        header: "Author",
        enableSorting: false,
        cell: (info) => {
          const original = info.row.original;
          if (original.__kind !== "participant") return null;

          const user = original.bot.user;
          return withAtag(
            "",
            `/authors/${getIDFromBase64(user.id, "UserType")}`,
            `View user profile for ${user.username}`,
            <span className="flex gap-1 items-center">
              <BotIcon user={user} /> {user.username}
            </span>
          );
        },
        meta: { priority: 3 },
      }),

      columnHelper.display({
        id: "winPerc",
        header: "Win %",
        enableSorting: false,
        cell: (info) => {
          const original = info.row.original;
          if (original.__kind !== "participant") return null;

          const val = original.winPerc ?? 0;
          return `${Math.trunc(val)} %`;
        },
        meta: { priority: 3 },
        size: 90,
      }),

      columnHelper.display({
        id: "stats",
        header: "Stats",
        enableSorting: false,
        cell: (info) => {
          const original = info.row.original;
          if (original.__kind !== "participant") return null;

          return withAtag(
            "View Stats",
            `/competitions/stats/${getIDFromBase64(
              original.id,
              "CompetitionParticipationType"
            )}`,
            `View stats ${original.id}`
          );
        },
        meta: { priority: 1 },
      }),
    ],
    [columnHelper]
  );

  const { loadMoreRef } = useInfiniteScroll(() => loadNext(50), hasNext);
  const [sorting, setSorting] = useState<SortingState>([]);

  const table = useReactTable({
    data: tableData,
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

  const hasItems = rankingsData.length > 0;

  return (
    <div>
      <Suspense fallback={<LoadingDots />}>
        <TableContainer table={table} loading={false} />
      </Suspense>

      {hasNext ? (
        <div className="flex justify-center mt-6" ref={loadMoreRef}>
          <LoadingMoreItems loadingMessage="Loading more bots..." />
        </div>
      ) : !hasNext && hasItems ? (
        <div className="mt-8">
          <NoMoreItems />
        </div>
      ) : null}
    </div>
  );
}
