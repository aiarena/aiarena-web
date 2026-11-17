import { graphql, useFragment } from "react-relay";
import {
  createColumnHelper,
  getCoreRowModel,
  SortingState,
  useReactTable,
  VisibilityState,
} from "@tanstack/react-table";
import { ReactNode, useMemo, useState, useTransition } from "react";
import { Link } from "react-router";
import { ArrowDownCircleIcon } from "@heroicons/react/24/outline";

import { getIDFromBase64, getNodes } from "@/_lib/relayHelpers";
import { reverseUrl } from "@/_lib/reverseUrl";
import { getDateTimeISOString } from "@/_lib/dateUtils";
import { getMatchResultParsed } from "@/_lib/parseMatchResult";
import { parseSort } from "@/_lib/tanstack_utils";
import { formatGameTime } from "@/_lib/formatGameTime";
import NoItemsInListMessage from "@/_components/_display/NoItemsInListMessage";
import { formatWinnerName } from "@/_components/_display/formatWinnerName";
import { useInfiniteScroll } from "@/_components/_hooks/useInfiniteScroll";
import { TableContainer } from "@/_components/_actions/TableContainer";
import LoadingMoreItems from "@/_components/_display/LoadingMoreItems";
import NoMoreItems from "@/_components/_display/NoMoreItems";
import SimpleToggle from "@/_components/_actions/_toggle/SimpleToggle";
import useStateWithLocalStorage from "@/_components/_hooks/useStateWithLocalStorage";
import { RenderRace } from "@/_components/_display/RenderRace";
import DownloadMap from "@/_components/_display/DownloadMap";
import TagSummaryWithModal from "@/_pages/Rework/Bot/BotResultsTable/TagSummaryModal";
import {
  MatchRequestsTable_matches$data,
  MatchRequestsTable_matches$key,
} from "./__generated__/MatchRequestsTable_matches.graphql";

/** What the owning connection is refetched with when sorting or the tag toggle changes. */
export type MatchRequestsQueryVars = {
  orderBy: string | null;
  showEveryonesTags: boolean;
};

interface MatchRequestsTableProps {
  matches: MatchRequestsTable_matches$key;
  hasNext: boolean;
  loadNext: (count: number) => void;
  /** Refetch the owning connection; called inside a transition. */
  refetch: (vars: MatchRequestsQueryVars) => void;
  /** localStorage key for the column visibility; one per page. */
  columnVisibilityKey: string;
  emptyMessage: ReactNode;
  /** On a bot's page, which lists competition and requested games alike, show
   *  where each match came from: its competition, or who requested it. */
  showOrigin?: boolean;
  /** Shown while the next page loads, e.g. "Loading more matches...". */
  loadingMoreMessage: string;
}

type MatchRow = MatchRequestsTable_matches$data[number];
type Participant = MatchRow["participant1"];

const columnHelper = createColumnHelper<MatchRow>();

// Table column id → MatchFilterSet order_by field.
const SORTING_MAP: Record<string, string> = {
  id: "id",
  participant1: "participant1__bot__name",
  participant2: "participant2__bot__name",
  result: "result__type",
  map: "map__name",
  started: "started",
  tags: "tags",
};

function ParticipantCell({
  participant,
  winnerName,
  hideSpoilers,
  role,
}: {
  participant: Participant;
  winnerName: string | undefined;
  hideSpoilers: boolean;
  role: string;
}) {
  const label = participant?.name || "";
  const content = (
    <span className="flex">
      <RenderRace withoutText race={participant?.playsRace} />
      {hideSpoilers ? label : formatWinnerName(winnerName, label)}
    </span>
  );
  const botId = getIDFromBase64(participant?.id, "BotType");

  return (
    <span className="flex justify-between">
      {botId ? (
        <Link
          className="font-semibold text-gray-200 truncate mr-2"
          to={reverseUrl("bot", { pk: botId })}
          role="cell"
          aria-label={`View bot profile for ${label}, ${role}`}
          title={label}
        >
          {content}
        </Link>
      ) : (
        <span className="font-semibold text-gray-200 truncate mr-2">
          {content}
        </span>
      )}
    </span>
  );
}

export default function MatchRequestsTable(props: MatchRequestsTableProps) {
  const matches = useFragment(
    graphql`
      fragment MatchRequestsTable_matches on MatchType @relay(plural: true) {
        id
        started
        requestedBy {
          id
          username
        }
        round {
          competition {
            id
            name
          }
        }
        participant1 {
          id
          name
          playsRace {
            name
            label
          }
        }
        participant2 {
          id
          name
          playsRace {
            name
            label
          }
        }
        result {
          type
          gameTimeFormatted
          replayFile
          winner {
            name
          }
        }
        # Which users' tags these are is decided by the owning connection's
        # showEveryonesTags filter, which prefetches them.
        tags {
          edges {
            node {
              id
              tag
              user {
                id
                username
              }
            }
          }
        }
        map {
          downloadLink
          name
        }
      }
    `,
    props.matches,
  );

  const { hasNext, loadNext, refetch, showOrigin = false } = props;

  const [columnVisibility, setColumnVisibility] =
    useStateWithLocalStorage<VisibilityState>(props.columnVisibilityKey, {});

  const [storedHideSpoilers] = useStateWithLocalStorage<boolean>(
    "Profile_Hide_Spoilers",
    false,
  );
  const hideSpoilers = storedHideSpoilers ?? false;

  const columns = useMemo(
    () => [
      columnHelper.accessor((row) => row.id, {
        id: "id",
        header: "Match ID",
        cell: (info) => {
          const matchId = getIDFromBase64(info.getValue(), "MatchType");
          return (
            <span className="flex justify-between">
              <Link
                className="font-semibold text-gray-200 truncate mr-2"
                to={reverseUrl("match", { pk: matchId })}
                role="cell"
                aria-label={`View match details for match ID ${matchId}`}
                title={matchId}
              >
                {matchId}
              </Link>
            </span>
          );
        },
        meta: { priority: 1 },
      }),

      columnHelper.accessor((row) => row.participant1?.name || "", {
        id: "participant1",
        header: "Bot",
        cell: (info) => (
          <ParticipantCell
            participant={info.row.original.participant1}
            winnerName={info.row.original.result?.winner?.name}
            hideSpoilers={hideSpoilers}
            role="Bot"
          />
        ),
        meta: { priority: 1 },
      }),

      columnHelper.accessor((row) => row.participant2?.name || "", {
        id: "participant2",
        header: "Opponent",
        cell: (info) => (
          <ParticipantCell
            participant={info.row.original.participant2}
            winnerName={info.row.original.result?.winner?.name}
            hideSpoilers={hideSpoilers}
            role="Opponent"
          />
        ),
        meta: { priority: 1 },
      }),

      ...(showOrigin
        ? [
            columnHelper.accessor(
              (row) =>
                row.round?.competition?.name ?? row.requestedBy?.username ?? "",
              {
                id: "origin",
                header: "Origin",
                enableSorting: false,
                cell: (info) => {
                  const competition = info.row.original.round?.competition;
                  if (competition) {
                    return (
                      <Link
                        className="font-semibold text-gray-200 truncate"
                        to={reverseUrl("competition", {
                          pk: getIDFromBase64(
                            competition.id,
                            "CompetitionType",
                          ),
                        })}
                        title={competition.name}
                      >
                        {competition.name}
                      </Link>
                    );
                  }
                  const requester = info.row.original.requestedBy;
                  if (!requester) {
                    return <span className="text-gray-400">Unknown</span>;
                  }
                  return (
                    <Link
                      className="font-semibold text-gray-200 truncate"
                      to={reverseUrl("author", {
                        pk: getIDFromBase64(requester.id, "UserType"),
                      })}
                      title={requester.username}
                    >
                      {requester.username}
                    </Link>
                  );
                },
                meta: { priority: 1 },
              },
            ),
          ]
        : []),

      columnHelper.accessor((row) => row.map?.name ?? "", {
        id: "map",
        header: "Map",
        cell: (info) => (
          <DownloadMap
            downloadLink={info.row.original.map?.downloadLink}
            name={info.getValue()}
          />
        ),
        meta: { priority: 1 },
      }),

      columnHelper.accessor((row) => row.result?.type, {
        id: "result",
        header: "Result",
        cell: (info) => {
          const result = getMatchResultParsed(
            info.getValue(),
            info.row.original.participant1?.name,
            info.row.original.participant2?.name,
          );
          return result !== "" ? result : "In Queue";
        },
        meta: { priority: 1 },
      }),

      columnHelper.accessor(
        (row) => formatGameTime(row.result?.gameTimeFormatted ?? ""),
        {
          id: "gameTime",
          header: "Duration",
          enableSorting: false,
          cell: (info) => info.getValue(),
          meta: { priority: 1 },
          size: 50,
        },
      ),

      columnHelper.accessor((row) => row.started ?? "", {
        id: "started",
        header: "Started",
        cell: (info) => {
          const time = getDateTimeISOString(info.getValue());
          return time !== "" ? time : "In Queue";
        },
        meta: { priority: 1 },
      }),

      columnHelper.accessor((row) => row.result?.replayFile ?? "", {
        id: "replay",
        header: "Replay",
        enableSorting: false,
        cell: (info) => {
          if (!info.getValue()) {
            return null;
          }
          const matchId = getIDFromBase64(info.row.original.id, "MatchType");
          return (
            <span className="flex justify-between">
              <Link
                className="font-semibold text-gray-200 truncate mr-2"
                to={info.getValue()}
                role="cell"
                aria-label={`Download replay file for Match ${matchId}`}
                title="Download"
              >
                <span className="flex items-center align-middle gap-1">
                  <span className="flex h-[25px] w-[25px] items-center align-middle">
                    <ArrowDownCircleIcon height={18} width={18} />
                  </span>
                  Replay
                </span>
              </Link>
            </span>
          );
        },
        meta: { priority: 1 },
        size: 50,
      }),

      columnHelper.accessor((row) => row.tags ?? "", {
        id: "tags",
        header: "Tags",
        enableSorting: false,
        cell: (info) => (
          <TagSummaryWithModal
            tagNodes={getNodes(info.row.original.tags)}
            previewCount={1}
            title={`Tags - Match Id: ${getIDFromBase64(
              info.row.original.id,
              "MatchType",
            )}`}
          />
        ),
        meta: { priority: 1 },
      }),
    ],
    [hideSpoilers, showOrigin],
  );

  const { loadMoreRef } = useInfiniteScroll(() => loadNext(50), hasNext);

  const [sorting, setSorting] = useState<SortingState>([]);
  const [showEveryonesTags, setShowEveryonesTags] = useState(false);
  const [isPending, startTransition] = useTransition();

  const refetchWith = (
    nextSorting: SortingState,
    nextShowEveryonesTags: boolean,
  ) => {
    startTransition(() => {
      refetch({
        orderBy: parseSort(SORTING_MAP, nextSorting),
        showEveryonesTags: nextShowEveryonesTags,
      });
    });
  };

  const table = useReactTable({
    data: matches as MatchRow[],
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
    onSortingChange: (updater) => {
      const next = typeof updater === "function" ? updater(sorting) : updater;
      setSorting(next);
      refetchWith(next, showEveryonesTags);
    },
    onColumnVisibilityChange: (updater) => {
      const next =
        typeof updater === "function"
          ? updater(columnVisibility ?? {})
          : updater;
      setColumnVisibility(next);
    },
  });

  const hasItems = matches.length > 0;

  return (
    <div>
      {hasItems ? (
        <TableContainer
          table={table}
          loading={isPending}
          appendHeader={
            <div
              className="flex gap-4 items-center"
              role="group"
              aria-label="Match filtering controls"
            >
              <div className="flex items-center gap-2">
                <span className="text-sm font-medium text-gray-300">
                  Show all tags
                </span>
                <SimpleToggle
                  enabled={showEveryonesTags}
                  onChange={() => {
                    const next = !showEveryonesTags;
                    setShowEveryonesTags(next);
                    refetchWith(sorting, next);
                  }}
                />
              </div>
            </div>
          }
        />
      ) : (
        <NoItemsInListMessage>{props.emptyMessage}</NoItemsInListMessage>
      )}

      {hasNext ? (
        <div className="flex justify-center mt-6" ref={loadMoreRef}>
          <LoadingMoreItems loadingMessage={props.loadingMoreMessage} />
        </div>
      ) : hasItems ? (
        <div className="mt-8">
          <NoMoreItems />
        </div>
      ) : null}
    </div>
  );
}
