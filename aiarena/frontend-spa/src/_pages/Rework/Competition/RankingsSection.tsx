import { graphql, usePaginationFragment } from "react-relay";
import { getIDFromBase64, getNodes } from "@/_lib/relayHelpers";
import { Suspense, useMemo, useState } from "react";
import {
  createColumnHelper,
  getCoreRowModel,
  SortingState,
  useReactTable,
  VisibilityState,
} from "@tanstack/react-table";
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
import { RenderRace } from "@/_components/_display/RenderRace";
import { Link } from "react-router";
import useStateWithLocalStorage from "@/_components/_hooks/useStateWithLocalStorage";

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
  const [columnVisibility, setColumnVisibility] =
    useStateWithLocalStorage<VisibilityState>(
      "Competition_RankingsSection_ColumnVisibility",
      {},
    );
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
    competition,
  );

  const rankingsData = useMemo(
    () => getNodes<ParticipationType>(data?.participants),
    [data],
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

  const columnHelper = useMemo(() => createColumnHelper<RankingsRow>(), []);
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

          const label = bot.name ?? "";
          const href = `/bots/${getIDFromBase64(bot.id, "BotType")}`;
          const aria = `View bot profile for ${bot.name}`;

          return (
            <span className="flex justify-between">
              <Link
                className="font-semibold text-gray-200 truncate mr-2"
                to={href}
                role="cell"
                aria-label={aria}
                title={`${label}`}
              >
                {label}
              </Link>
            </span>
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

          return <RenderRace race={original.bot.playsRace} />;
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

          const label = "";
          const href = `/authors/${getIDFromBase64(user.id, "UserType")}`;
          const aria = `View user profile for ${user.username}`;
          const children = (
            <span className="flex gap-1 items-center">
              <BotIcon user={user} /> {user.username}
            </span>
          );

          return (
            <span className="flex justify-between">
              <Link
                className="font-semibold text-gray-200 truncate mr-2"
                to={href}
                role="cell"
                aria-label={aria}
                title={`${label}`}
              >
                {children ? children : label}
              </Link>
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

          const label = "View Stats";
          const href = `/competitions/stats/${getIDFromBase64(
            original.id,
            "CompetitionParticipationType",
          )}`;
          const aria = `View stats ${original.id}`;

          return (
            <span className="flex justify-between">
              <Link
                className="font-semibold text-gray-200 truncate mr-2"
                to={href}
                role="cell"
                aria-label={aria}
                title={`${label}`}
              >
                {label}
              </Link>
            </span>
          );

          // return <StatsButton id={original.id} />;
        },
        meta: { priority: 1 },
      }),
    ],
    [columnHelper],
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
    initialState: {
      columnVisibility: columnVisibility ?? undefined,
    },
    state: {
      sorting,
      columnVisibility: columnVisibility ?? {},
    },
    onSortingChange: setSorting,
    onColumnVisibilityChange: (updater) => {
      const next =
        typeof updater === "function"
          ? updater(columnVisibility ?? {})
          : updater;
      setColumnVisibility(next);
    },
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
