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

interface RankingsSectionProps {
  competition: RankingsSection_competition$key;
}

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
                playsRace
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

  type ParticipationType = NonNullable<
    NonNullable<
      NonNullable<
        RankingsSection_competition$data["participants"]
      >["edges"][number]
    >["node"]
  >;

  const rankingsData = useMemo(
    () => getNodes<ParticipationType>(data?.participants),
    [data]
  );

  const columnHelper = createColumnHelper<ParticipationType>();

  const columns = useMemo(
    () => [
      columnHelper.accessor((row) => row.elo || "", {
        id: "index",
        header: "Rank",
        enableSorting: false,
        cell: ({ cell }) => cell.row.index + 1,
        meta: { priority: 1 },
        size: 5,
      }),
      columnHelper.accessor((row) => row.divisionNum ?? "", {
        id: "divisionNum",
        header: "Division",
        enableSorting: false,
        cell: (info) => info.getValue(),
        meta: { priority: 1 },
        size: 5,
      }),
      columnHelper.accessor((row) => row.bot.name || "", {
        id: "name",
        header: "Name",
        enableSorting: false,
        cell: (info) =>
          withAtag(
            info.getValue(),
            `/bots/${getIDFromBase64(info.row.original.bot.id, "BotType")}`,
            `View bot profile for ${info.row.original.bot.name}`
          ),
        meta: { priority: 1 },
      }),
      columnHelper.accessor((row) => row.bot.playsRace ?? "", {
        id: "playsRace",
        header: "Race",
        enableSorting: false,
        cell: (row) => row.getValue() || "--",
        meta: { priority: 1 },
      }),
      columnHelper.accessor((row) => row.bot.type ?? "", {
        id: "type",
        header: "Type",
        enableSorting: false,
        cell: (row) => row.getValue() || "--",
        meta: { priority: 1 },
      }),
      columnHelper.accessor((row) => row.bot.user.username ?? "", {
        id: "username",
        header: "Author",
        enableSorting: false,

        cell: (info) =>
          withAtag(
            "",
            `/authors/${getIDFromBase64(info.row.original.bot.user.id, "UserType")}`,
            `View user profile for ${info.row.original.bot.user.username}`,
            <span className="flex gap-1 items-center">
              <BotIcon user={info.row.original.bot.user} /> {info.getValue()}
            </span>
          ),

        meta: { priority: 1 },
      }),

      columnHelper.accessor((row) => row.elo ?? "", {
        id: "elo",
        header: "ELO",
        enableSorting: false,

        cell: (info) => {
          const eloChange = info.row.original.trend;
          return (
            <span
              className="flex items-center gap-1 "
              title={`ELO changed ${eloChange} in the last 30 games`}
            >
              {info.getValue()}
              <EloTrendIcon trend={eloChange} />
            </span>
          );
        },

        meta: { priority: 1 },
        size: 100,
      }),

      columnHelper.accessor((row) => row.winPerc ?? "", {
        id: "winPerc",
        header: "Win %",
        enableSorting: false,
        cell: (info) => {
          return `${Math.trunc(info.getValue())} %`;
        },
        meta: { priority: 1 },
        size: 90,
      }),

      columnHelper.accessor((row) => row.id || "", {
        id: "stats",
        header: "Stats",
        enableSorting: false,
        cell: (info) => {
          return withAtag(
            "View Stats",
            `/competitions/stats/${getIDFromBase64(info.getValue(), "CompetitionParticipationType")}`,
            `View stats ${info.getValue()}`
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
    data: rankingsData,
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
