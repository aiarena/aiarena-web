import {
  ColumnDef,
  createColumnHelper,
  getCoreRowModel,
  SortingState,
  useReactTable,
  VisibilityState,
} from "@tanstack/react-table";

import { getIDFromBase64, getNodes } from "@/_lib/relayHelpers";
import clsx from "clsx";

import { useEffect, useMemo, useRef, useState } from "react";

import { parseSort } from "@/_lib/tanstack_utils";

import WatchYourGamesButton from "@/_components/_actions/WatchYourGamesButton";

import ResultsFiltersModal from "../_modals/ResultsFiltersModal";
import WatchGamesModal from "@/_pages/UserMatchRequests/UserMatchRequests/_modals/WatchGamesModal";
import { getDateTimeISOString } from "@/_lib/dateUtils";
import { ArrowDownCircleIcon, FunnelIcon } from "@heroicons/react/24/outline";
import { CoreBotRaceLabelChoices } from "@/_pages/UserBots/UserBotsSection/_modals/__generated__/UploadBotModalQuery.graphql";
import EloChange from "@/_components/_display/EloChange";
import StepTime from "@/_components/_display/RenderStepTime";
import { RenderResult } from "@/_components/_display/RenderResult";
import { RenderResultCause } from "@/_components/_display/RenderResultCause";
import { HardcodedMatchTypeOptions } from "../CustomOptions/MatchTypeOptions";
import { RenderRace } from "@/_components/_display/RenderRace";
import ButtonToggle from "@/_components/_actions/_toggle/ButtonToggle";
import { TableContainerShell } from "@/_components/_actions/TableContainerShell";
import { BotResultsRefetchArgs, BotResultsTbody } from "./BotResultsTbody";
import {
  BotResultsTbody_bot$data,
  BotResultsTbody_bot$key,
  CoreMatchParticipationResultCauseChoices,
  CoreMatchParticipationResultChoices,
} from "./__generated__/BotResultsTbody_bot.graphql";
import { BotResultsTableSortingMap } from "./botResultTableSearchParams";
import TagSummaryWithModal from "./TagSummaryModal";
import { Link } from "react-router";
import useStateWithLocalStorage from "@/_components/_hooks/useStateWithLocalStorage";

interface BotResultsTableProps {
  data: BotResultsTbody_bot$key;
  filterPreset?: { competitionId?: string; competitionName?: string };
  onApplyFilters?: (next: ResultsFilters, replace?: boolean) => void;
  initialFilters?: ResultsFilters;
  onApplySort?: (next: SortingState, replace?: boolean) => void;
  initialSorting?: SortingState;
  botZipUpdated: string;
}

function getBotEloChange(
  participant1: NonNullable<MatchResult["participant1"]> | null | undefined,
  participant2: NonNullable<MatchResult["participant1"]> | null | undefined,
  bot: NonNullable<NonNullable<MatchParticipation>["bot"]> | null | undefined,
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
  bot: NonNullable<NonNullable<MatchParticipation>["bot"]> | null | undefined,
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
  matchStartedAfter: string | undefined; // ISO string
  matchStartedBefore: string | undefined; // ISO string
  tags: string | undefined;
  searchOnlyMyTags: boolean | undefined;
  showEveryonesTags: boolean | undefined;
  includeStarted: boolean | undefined;
  includeQueued: boolean | undefined;
  includeFinished: boolean | undefined;
}

export type BotResultsRow = NonNullable<
  NonNullable<
    NonNullable<
      BotResultsTbody_bot$data["matchParticipations"]
    >["edges"][number]
  >["node"]
>;

type MatchParticipation = NonNullable<
  NonNullable<BotResultsTbody_bot$data["matchParticipations"]>["edges"][number]
>["node"];

type Match = NonNullable<NonNullable<MatchParticipation>["match"]>;

type MatchResult = NonNullable<NonNullable<Match>["result"]>;

type TagNode = NonNullable<NonNullable<MatchParticipation>["match"]>["tags"];

export type Tag = NonNullable<
  NonNullable<NonNullable<TagNode>["edges"]>[number]
>["node"];

export default function BotResultsTable(props: BotResultsTableProps) {
  const [sorting, setSorting] = useState<SortingState>(
    () => props.initialSorting ?? [],
  );

  const [columnVisibility, setColumnVisibility] =
    useStateWithLocalStorage<VisibilityState>(
      "Bot_BotResultsTable_ColumnVisibility",
      {},
    );

  const [columnSizing, setColumnSizing] = useState({});

  const [isWatchGamesModalOpen, setIsWatchGamesModalOpen] = useState(false);
  const [isFiltersModalOpen, setIsFiltersModalOpen] = useState(false);

  const defaultFilters: ResultsFilters = {
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
    competitionId: props.filterPreset?.competitionId || undefined,
    competitionName: props.filterPreset?.competitionName || undefined,
    matchStartedAfter: props.botZipUpdated,
    matchStartedBefore: undefined,
    tags: undefined,
    searchOnlyMyTags: undefined,
    showEveryonesTags: undefined,
    includeStarted: false,
    includeQueued: false,
    includeFinished: true,
  };

  const [filters, setFilters] = useState<ResultsFilters>(() => {
    return props.initialFilters
      ? { ...defaultFilters, ...props.initialFilters }
      : defaultFilters;
  });

  useEffect(() => {
    if (props.initialSorting) setSorting(props.initialSorting);
  }, [props.initialSorting]);

  const columnHelper = createColumnHelper<BotResultsRow>();
  const columns = useMemo(
    () => [
      columnHelper.accessor((row) => row.match.id, {
        id: "id",
        header: "ID",
        enableSorting: true,
        cell: (info) => {
          const label = getIDFromBase64(info.getValue(), "MatchType") || "";
          const href = `/matches/${getIDFromBase64(info.getValue(), "MatchType")}`;
          const aria = `View match details for Match ID ${getIDFromBase64(info.getValue(), "MatchType")}`;

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
        size: 50,
      }),

      columnHelper.accessor(
        (row) =>
          getOpponent(row.match?.participant1, row.match?.participant2, row.bot)
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
              bot,
            )?.opponent;

            const label = opponent?.name || "";
            const href = `/bots/${getIDFromBase64(opponent?.id, "BotType")}`;
            const aria = `View bot profile for ${opponent?.name}, Bot`;

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
          size: 100,
        },
      ),
      columnHelper.accessor(
        (row) =>
          getOpponent(row.match?.participant1, row.match?.participant2, row.bot)
            ?.opponent?.name || "",
        {
          id: "opponent_race",
          header: "Opponent Race",
          enableSorting: false,
          cell: (info) => {
            const bot = info.row.original.bot;
            const participant1 = info.row.original.match?.participant1;
            const participant2 = info.row.original.match?.participant2;
            const opponent = getOpponent(
              participant1,
              participant2,
              bot,
            )?.opponent;

            return <RenderRace race={opponent?.playsRace} />;
          },
          meta: { priority: 1 },
          size: 50,
        },
      ),
      columnHelper.accessor((row) => row.result ?? "", {
        id: "result",
        header: "Result",
        enableSorting: false,
        cell: (info) => {
          return <RenderResult result={info.getValue()} />;
        },
        meta: { priority: 1 },
        size: 50,
      }),

      columnHelper.accessor(
        (row) =>
          getBotEloChange(
            row.match.result?.participant1,
            row.match.result?.participant2,
            row.bot,
          )?.eloChange,
        {
          id: "elo_change",
          header: "Elo +/-",
          enableSorting: false,
          cell: (info) => {
            return <EloChange delta={info.getValue()} />;
          },
          meta: { priority: 1 },
          size: 50,
        },
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
        size: 50,
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
          size: 50,
        },
      ),
      columnHelper.accessor((row) => row.match.result?.created ?? "", {
        id: "date",
        header: "Date",
        enableSorting: false,
        cell: (info) => {
          return getDateTimeISOString(info.getValue()) || "";
        },
        meta: { priority: 1 },
        size: 50,
      }),
      columnHelper.accessor((row) => row.match.result?.replayFile ?? "", {
        id: "replay",
        header: "Replay",
        enableSorting: false,
        cell: (info) => {
          if (info.getValue()) {
            const label = "Download";
            const href = `${info.getValue()}`;
            const aria = `Download replay file for Match ${info.row.original.match.id}`;
            const children = (
              <span className="flex items-center align-middle gap-1">
                <span className="flex h-[25px] w-[25px] items-center align-middle">
                  <ArrowDownCircleIcon height={18} width={18} />
                </span>
                Replay
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
          }
        },
        meta: { priority: 1 },
        size: 50,
      }),
      columnHelper.accessor((row) => row.matchLog ?? "", {
        id: "log",
        header: "Match Log",

        enableSorting: false,
        cell: (info) => {
          if (info.getValue() != "") {
            const label = "Download";
            const href = `/${info.getValue()}`;
            const aria = `Download match log for Match ${info.row.original.match.id}`;
            const children = (
              <span className="flex items-center align-middle gap-1">
                <span className="flex h-[25px] w-[25px] items-center align-middle">
                  <ArrowDownCircleIcon height={18} width={18} />
                </span>
                Log
              </span>
            );

            return (
              <span className="flex justify-between">
                <a
                  className="font-semibold text-gray-200 truncate mr-2"
                  href={href}
                  role="cell"
                  aria-label={aria}
                  download
                  title={`${label}`}
                >
                  {children ? children : label}
                </a>
              </span>
            );
          }
        },
        meta: { priority: 1 },
        size: 50,
      }),
      columnHelper.accessor((row) => row.match.tags ?? "", {
        id: "tags",
        header: "Tags",
        enableSorting: false,
        cell: (info) => {
          const nodes = getNodes(info.row.original.match.tags);

          return (
            <TagSummaryWithModal
              tagNodes={nodes}
              previewCount={1}
              title={`Tags - Match Id: ${getIDFromBase64(info.row.original.match.id, "MatchType")}`}
            />
          );
        },
        meta: { priority: 1 },
      }),
    ],
    [columnHelper],
  );

  const headerTable = useReactTable({
    data: [],
    columns,
    getCoreRowModel: getCoreRowModel(),
    enableColumnResizing: true,
    columnResizeMode: "onChange",
    manualSorting: true,
    enableSorting: true,
    initialState: {
      columnVisibility: columnVisibility ?? undefined,
    },

    state: { columnVisibility: columnVisibility ?? {}, columnSizing, sorting },
    onColumnVisibilityChange: (updater) => {
      const next =
        typeof updater === "function"
          ? updater(columnVisibility ?? {})
          : updater;
      setColumnVisibility(next);
    },
    onColumnSizingChange: setColumnSizing,
    onSortingChange: (updater) => {
      setSorting((prev) => {
        const next = typeof updater === "function" ? updater(prev) : updater;

        props.onApplySort?.(next, true);
        runRefetch(filters, next);

        return next;
      });
    },
  });
  function apply(next: ResultsFilters, replace = true) {
    setFilters(next);
    props.onApplyFilters?.(next, replace);
    runRefetch(next, sorting);
  }

  const refetchFnRef = useRef<null | ((args: BotResultsRefetchArgs) => void)>(
    null,
  );

  function runRefetch(nextFilters: ResultsFilters, nextSorting: SortingState) {
    const fn = refetchFnRef.current;
    if (!fn) return;

    const orderBy = parseSort(BotResultsTableSortingMap, nextSorting) || "-id";

    fn({ filters: nextFilters, orderBy });
  }
  const allColumns = headerTable.getAllLeafColumns();
  const visibleColumnCount = allColumns.filter((c) => c.getIsVisible()).length;

  const excludedKeys = new Set([
    "includeStarted",
    "includeQueued",
    "includeFinished",
  ]);

  const filterIsActive = Object.entries(filters).some(
    ([key, value]) => !excludedKeys.has(key) && value !== undefined,
  );

  return (
    <div>
      <TableContainerShell
        headerTable={headerTable}
        appendLeftHeader={
          <div className="flex flex-wrap gap-2">
            <button
              className={clsx(
                "inline-flex items-center  justify-center gap-x-1.5 rounded-md border-2 transition duration-100 ease-in-out transform",
                "px-2 py-2 font-semibold bg-neutral-900 shadow-xs border",
                filterIsActive
                  ? "border-customGreen text-gray-200"
                  : "border-neutral-700 text-gray-400",
                "hover:border-customGreen",
              )}
              onClick={() => setIsFiltersModalOpen(true)}
            >
              <FunnelIcon className={clsx("size-5", "text-gray-400")} />
            </button>
            <ButtonToggle
              active={filters.includeQueued}
              onClick={() =>
                apply({ ...filters, includeQueued: !filters.includeQueued })
              }
              text="Queued"
            />

            <ButtonToggle
              active={filters.includeStarted}
              onClick={() =>
                apply({ ...filters, includeStarted: !filters.includeStarted })
              }
              text="Playing"
            />

            <ButtonToggle
              active={filters.includeFinished}
              onClick={() =>
                apply({ ...filters, includeFinished: !filters.includeFinished })
              }
              text="Finished"
            />
            <ButtonToggle
              active={!!filters.matchStartedAfter}
              onClick={() =>
                apply({
                  ...filters,
                  matchStartedAfter: filters.matchStartedAfter
                    ? undefined
                    : props.botZipUpdated,
                })
              }
              text="Since Updated"
            />
          </div>
        }
        appendHeader={
          <div>
            <WatchYourGamesButton
              onClick={() => setIsWatchGamesModalOpen(true)}
            >
              <span>Watch Replays on Twitch</span>
            </WatchYourGamesButton>
          </div>
        }
        tbody={
          <BotResultsTbody
            fragmentRef={props.data}
            columnCount={visibleColumnCount}
            columns={columns as unknown as ColumnDef<BotResultsRow, unknown>[]}
            state={{ columnVisibility: columnVisibility ?? {}, columnSizing }}
            onState={{
              setColumnVisibility: (updater) => {
                const next =
                  typeof updater === "function"
                    ? updater(columnVisibility ?? {})
                    : updater;
                setColumnVisibility(next);
              },
              setColumnSizing,
            }}
            exposeRefetch={(fn) => {
              refetchFnRef.current = fn;
            }}
          />
        }
      />

      <WatchGamesModal
        isOpen={isWatchGamesModalOpen}
        onClose={() => setIsWatchGamesModalOpen(false)}
      />
      <ResultsFiltersModal
        isOpen={isFiltersModalOpen}
        onClose={() => setIsFiltersModalOpen(false)}
        filters={filters}
        setFilters={setFilters}
        onApply={(next) => apply(next, true)}
        botZipUpdated={props.botZipUpdated}
      />
    </div>
  );
}
