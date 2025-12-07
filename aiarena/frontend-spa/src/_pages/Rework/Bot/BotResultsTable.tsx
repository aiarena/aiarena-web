import { graphql, usePaginationFragment } from "react-relay";
import {
  createColumnHelper,
  getCoreRowModel,
  useReactTable,
} from "@tanstack/react-table";

import { getIDFromBase64, getNodes } from "@/_lib/relayHelpers";
import clsx from "clsx";

import { Suspense, useMemo, useState, useTransition } from "react";

import { withAtag } from "@/_lib/tanstack_utils";

import NoMoreItems from "@/_components/_display/NoMoreItems";
import LoadingMoreItems from "@/_components/_display/LoadingMoreItems";
import { TableContainer } from "@/_components/_actions/TableContainer";
import LoadingDots from "@/_components/_display/LoadingDots";
import { useInfiniteScroll } from "@/_components/_hooks/useInfiniteScroll";

import WatchYourGamesButton from "@/_components/_actions/WatchYourGamesButton";
import {
  BotResultsTable_bot$data,
  BotResultsTable_bot$key,
  CoreMatchParticipationResultCauseChoices,
  CoreMatchParticipationResultChoices,
} from "./__generated__/BotResultsTable_bot.graphql";
import ResultsFiltersModal from "./_modals/ResultsFiltersModal";
import WatchGamesModal from "@/_pages/UserMatchRequests/UserMatchRequests/_modals/WatchGamesModal";
import { getDateTimeISOString } from "@/_lib/dateUtils";
import {
  ArrowDownCircleIcon,
  MagnifyingGlassIcon,
} from "@heroicons/react/24/outline";
import { CoreBotRaceLabelChoices } from "@/_pages/UserBots/UserBotsSection/_modals/__generated__/UploadBotModalQuery.graphql";
import EloChange from "@/_components/_display/EloChange";
import StepTime from "@/_components/_display/RenderStepTime";
import { RenderResult } from "@/_components/_display/RenderResult";
import { RenderResultCause } from "@/_components/_display/RenderResultCause";
import { HardcodedMatchTypeOptions } from "./CustomOptions/MatchTypeOptions";

interface BotResultsTableProps {
  data: BotResultsTable_bot$key;
}

type MatchParticipation = NonNullable<
  NonNullable<BotResultsTable_bot$data["matchParticipations"]>["edges"][number]
>["node"];
type Match = NonNullable<NonNullable<MatchParticipation>["match"]>;

type MatchResult = NonNullable<NonNullable<Match>["result"]>;

function getBotEloChange(
  participant1: NonNullable<MatchResult["participant1"]> | null | undefined,
  participant2: NonNullable<MatchResult["participant1"]> | null | undefined,
  bot: NonNullable<NonNullable<MatchParticipation>["bot"]> | null | undefined
) {
  if (!bot) return undefined;

  if (participant1 && bot.id === participant1.bot.id) {
    return {
      eloChange: participant1.eloChange,
    };
  }

  if (participant2 && bot.id === participant2.bot.id) {
    return {
      eloChange: participant2.eloChange,
    };
  }

  return undefined;
}

function getOpponent(
  participant1: NonNullable<Match["participant1"]> | null | undefined,
  participant2: NonNullable<Match["participant1"]> | null | undefined,
  bot: NonNullable<NonNullable<MatchParticipation>["bot"]> | null | undefined
) {
  if (!bot) return undefined;

  if (participant1 && bot.id === participant1.id) {
    return {
      opponent: participant2 ?? undefined,
      bot: participant1 ?? undefined,
    };
  }

  if (participant2 && bot.id === participant2.id) {
    return {
      opponent: participant1 ?? undefined,
      bot: participant2 ?? undefined,
    };
  }

  return undefined;
}

export interface ResultsFilters {
  opponentName: string | undefined;
  opponentId: string | undefined;
  opponentPlaysRaceId: CoreBotRaceLabelChoices | undefined;
  opponentPlaysRaceName: string | undefined;

  result: CoreMatchParticipationResultChoices | undefined;
  cause: CoreMatchParticipationResultCauseChoices | undefined;
  avgStepTimeMin?: number | null;
  avgStepTimeMax?: number | null;
  gameTimeMin: number | undefined;
  gameTimeMax: number | undefined;
  matchType: HardcodedMatchTypeOptions | undefined;
  mapName: string | undefined;
  competitionId: string | undefined;
  competitionName: string | undefined;
}

export default function BotResultsTable(props: BotResultsTableProps) {
  const [isFiltersMoodalOpen, setIsFiltersModalOpen] = useState(false);

  const [filters, setFilters] = useState<ResultsFilters>({
    opponentName: undefined,
    opponentId: undefined,
    opponentPlaysRaceId: undefined,
    opponentPlaysRaceName: undefined,
    result: undefined,
    cause: undefined,
    avgStepTimeMin: undefined,
    avgStepTimeMax: undefined,
    gameTimeMin: undefined,
    gameTimeMax: undefined,
    matchType: undefined,
    mapName: undefined,
    competitionId: undefined,
    competitionName: undefined,
  });

  const { data, loadNext, hasNext, refetch } = usePaginationFragment(
    graphql`
      fragment BotResultsTable_bot on BotType
      @refetchable(queryName: "BotResultsTablePaginationQuery")
      @argumentDefinitions(
        cursor: { type: "String" }
        first: { type: "Int", defaultValue: 50 }
        orderBy: { type: "String", defaultValue: "-id" }
        opponentId: { type: "String" }
        opponentPlaysRace: { type: "String" }
        result: { type: "String" }
        cause: { type: "String" }
        avgStepTimeMin: { type: "Decimal" }
        avgStepTimeMax: { type: "Decimal" }
        gameTimeMin: { type: "Decimal" }
        gameTimeMax: { type: "Decimal" }
        matchType: { type: "String" }
        mapName: { type: "String" }
        competitionId: { type: "String" }
      ) {
        matchParticipations(
          first: $first
          after: $cursor
          orderBy: $orderBy
          opponentId: $opponentId
          opponentPlaysRace: $opponentPlaysRace
          result: $result
          cause: $cause
          avgStepTimeMin: $avgStepTimeMin
          avgStepTimeMax: $avgStepTimeMax
          gameTimeMax: $gameTimeMax
          gameTimeMin: $gameTimeMin
          matchType: $matchType
          mapName: $mapName
          competitionId: $competitionId
        ) @connection(key: "ResultsTable_node_matchParticipations") {
          totalCount
          edges {
            node {
              id
              result
              resultCause
              avgStepTime
              eloChange
              bot {
                id
                name
                playsRace {
                  name
                  label
                  id
                }
              }
              match {
                id
                started
                status
                participant1 {
                  name
                  id
                }
                participant2 {
                  name
                  id
                }
                map {
                  id
                  name
                }
                round {
                  competition {
                    id
                    name
                  }
                }
                result {
                  created
                  type
                  gameTimeFormatted
                  replayFile

                  participant1 {
                    eloChange
                    id
                    bot {
                      name
                      id
                    }
                    result
                  }
                  participant2 {
                    eloChange
                    id
                    bot {
                      name
                      id
                    }
                    result
                  }
                }
              }
            }
          }
        }
      }
    `,

    props.data as BotResultsTable_bot$key
  );

  function handleSort() {
    startTransition(() => {
      refetch({
        opponentId: filters.opponentId,
        opponentPlaysRace: filters.opponentPlaysRaceId,
        result: filters.result?.toLowerCase(),
        cause: filters.cause?.toLowerCase(),
        avgStepTimeMin: filters.avgStepTimeMin,
        avgStepTimeMax: filters.avgStepTimeMax,
        gameTimeMin: filters.gameTimeMin,
        gameTimeMax: filters.gameTimeMax,
        matchType: filters.matchType?.toLowerCase(),
        mapName: filters.mapName,
        competitionId: filters.competitionId,
        orderBy: "-id",
        first: 50,
      });
    });
  }

  type ResultType = NonNullable<
    NonNullable<
      NonNullable<
        BotResultsTable_bot$data["matchParticipations"]
      >["edges"][number]
    >["node"]
  >;
  const [isWatchGamesModalOpen, setIsWatchGamesModalOpen] = useState(false);

  const [isPending, startTransition] = useTransition();
  const matchParticipationData = useMemo(
    () => getNodes<ResultType>(data?.matchParticipations),
    [data]
  );

  const columnHelper = createColumnHelper<ResultType>();

  const columns = useMemo(
    () => [
      columnHelper.accessor((row) => row.match.id, {
        id: "id",
        header: "ID",
        enableSorting: false,
        cell: (info) =>
          withAtag(
            getIDFromBase64(info.getValue(), "MatchType") || "",
            `/matches/${getIDFromBase64(info.getValue(), "MatchType")}`,
            `View match details for Match ID ${info.getValue()}`
          ),
        meta: { priority: 1 },
        size: 125,
      }),

      columnHelper.accessor(
        (row) =>
          getOpponent(row.match?.participant1, row.match?.participant1, row.bot)
            ?.opponent?.name || "",
        {
          id: "opponent",
          header: "Opponent",
          enableSorting: false,
          cell: (info) => {
            const bot = info.row.original.bot;
            const participant1 = info.row.original.match?.participant1;
            const participant2 = info.row.original.match?.participant2;
            const opponent = getOpponent(
              participant1,
              participant2,
              bot
            )?.opponent;

            return withAtag(
              opponent?.name || "",
              `/bots/${getIDFromBase64(opponent?.id, "BotType")}`,
              `View bot profile for ${opponent?.name}, Bot`
            );
          },
          meta: { priority: 1 },
        }
      ),
      columnHelper.accessor((row) => row.result ?? "", {
        id: "result",
        header: "Result",
        enableSorting: false,
        cell: (info) => {
          return <RenderResult result={info.getValue()} />;
        },
        meta: { priority: 1 },
        size: 5,
      }),

      columnHelper.accessor(
        (row) =>
          getBotEloChange(
            row.match.result?.participant1,
            row.match.result?.participant2,
            row.bot
          )?.eloChange,
        {
          id: "elo_change",
          header: "Elo +/-",
          enableSorting: false,
          cell: (info) => {
            console.log("elochange ", info.row);
            return <EloChange delta={info.getValue()} />;
          },
          meta: { priority: 1 },
          size: 85,
        }
      ),
      columnHelper.accessor((row) => row.resultCause, {
        id: "cause",
        header: "Cause",
        enableSorting: false,
        cell: (info) => {
          if (info.getValue()) {
            return <RenderResultCause cause={info.getValue()} />;
          } else {
            return info.row.original.match.status;
          }
        },
        meta: { priority: 1 },
        size: 100,
      }),
      columnHelper.accessor((row) => row.avgStepTime ?? "", {
        id: "step",
        header: "Avg Step",
        enableSorting: false,
        cell: (info) => {
          if (info.getValue()) {
            return <StepTime time={info.getValue()} />;
          }
        },
        meta: { priority: 1 },
        size: 100,
      }),
      columnHelper.accessor(
        (row) => row.match.result?.gameTimeFormatted ?? "",
        {
          id: "duration",
          header: "Duration",
          enableSorting: false,
          cell: (info) => {
            return info.getValue();
          },
          meta: { priority: 1 },
          size: 5,
        }
      ),
      columnHelper.accessor((row) => row.match.result?.created ?? "", {
        id: "date",
        header: "Date",
        enableSorting: false,
        cell: (info) => {
          return getDateTimeISOString(info.getValue()) || "";
        },
        meta: { priority: 1 },
      }),
      columnHelper.accessor((row) => row.match.result?.replayFile ?? "", {
        id: "replay",
        header: "Replay",
        enableSorting: false,
        cell: (info) => {
          if (info.getValue()) {
            return withAtag(
              "Download",
              `${info.getValue()}`,
              `Download replay file for Match ${info.row.original.match.id}`,
              <span className="flex items-center gap-1">
                <ArrowDownCircleIcon height={18} /> Download
              </span>
            );
          }
        },
        meta: { priority: 1 },
        size: 110,
      }),
    ],
    [columnHelper]
  );

  const { loadMoreRef } = useInfiniteScroll(() => loadNext(100), hasNext);

  const table = useReactTable({
    data: matchParticipationData,
    columns,
    getCoreRowModel: getCoreRowModel(),
    enableColumnResizing: true,
    columnResizeMode: "onChange",
    manualSorting: true,
  });

  const hasItems = matchParticipationData.length > 0;

  return (
    <div>
      <Suspense fallback={<LoadingDots />}>
        <TableContainer
          table={table}
          loading={isPending}
          appendLeftHeader={
            <>
              <button
                className="inline-flex w-full justify-center gap-x-1.5 rounded-md 
                px-3 py-3 font-semibold bg-neutral-900 shadow-xs border border-neutral-700 
                ring-1 ring-inset ring-gray-700 focus:outline-none focus:ring-customGreen focus:ring-2"
                onClick={() => setIsFiltersModalOpen(true)}
              >
                <MagnifyingGlassIcon
                  className={clsx("size-5", "text-gray-400")}
                />
              </button>
            </>
          }
          appendHeader={
            <>
              <WatchYourGamesButton
                onClick={() => setIsWatchGamesModalOpen(true)}
              >
                <span>Watch Replays on Twitch</span>
              </WatchYourGamesButton>
            </>
          }
        />
      </Suspense>

      {hasNext ? (
        <div className="flex justify-center mt-6" ref={loadMoreRef}>
          <LoadingMoreItems loadingMessage="Loading more results..." />
        </div>
      ) : !hasNext && hasItems ? (
        <div className="mt-8">
          <NoMoreItems />
        </div>
      ) : null}
      <WatchGamesModal
        isOpen={isWatchGamesModalOpen}
        onClose={() => setIsWatchGamesModalOpen(false)}
      />
      <ResultsFiltersModal
        isOpen={isFiltersMoodalOpen}
        onClose={() => setIsFiltersModalOpen(false)}
        filters={filters}
        setFilters={setFilters}
        onApply={handleSort}
      />
    </div>
  );
}
