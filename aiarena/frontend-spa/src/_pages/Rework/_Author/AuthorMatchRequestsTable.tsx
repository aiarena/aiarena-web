import { graphql, usePaginationFragment } from "react-relay";
import {
  createColumnHelper,
  getCoreRowModel,
  SortingState,
  useReactTable,
  VisibilityState,
} from "@tanstack/react-table";

import { getIDFromBase64, getNodes } from "@/_lib/relayHelpers";
import { reverseUrl } from "@/_lib/reverseUrl";

import { Suspense, useEffect, useMemo, useState, useTransition } from "react";
import { getDateTimeISOString } from "@/_lib/dateUtils";

import { getMatchResultParsed } from "@/_lib/parseMatchResult";
import { parseSort } from "@/_lib/tanstack_utils";

import NoItemsInListMessage from "@/_components/_display/NoItemsInListMessage";
import { formatWinnerName } from "@/_components/_display/formatWinnerName";
import { useInfiniteScroll } from "@/_components/_hooks/useInfiniteScroll";
import LoadingDots from "@/_components/_display/LoadingDots";
import { TableContainer } from "@/_components/_actions/TableContainer";
import LoadingMoreItems from "@/_components/_display/LoadingMoreItems";
import NoMoreItems from "@/_components/_display/NoMoreItems";
import SimpleToggle from "@/_components/_actions/_toggle/SimpleToggle";
import { Link } from "react-router";
import useStateWithLocalStorage from "@/_components/_hooks/useStateWithLocalStorage";
import { RenderRace } from "@/_components/_display/RenderRace";
import { ArrowDownCircleIcon } from "@heroicons/react/24/outline";
import TagSummaryWithModal from "../Bot/BotResultsTable/TagSummaryModal";
import DownloadMap from "@/_components/_display/DownloadMap";
import {
  AuthorMatchRequestsTable_user$data,
  AuthorMatchRequestsTable_user$key,
} from "./__generated__/AuthorMatchRequestsTable_user.graphql";

interface AuthorMatchRequestsTableProps {
  data: AuthorMatchRequestsTable_user$key;
}

export default function AuthorMatchRequestsTable(
  props: AuthorMatchRequestsTableProps,
) {
  const [columnVisibility, setColumnVisibility] =
    useStateWithLocalStorage<VisibilityState>(
      "Author_AuthorMatchRequestsTable_ColumnVisibility",
      {},
    );

  const [hideSpoilers] = useStateWithLocalStorage<boolean>(
    "Profile_Hide_Spoilers",
    false,
  );

  const { data, loadNext, hasNext, refetch } = usePaginationFragment(
    graphql`
      fragment AuthorMatchRequestsTable_user on UserType
      @refetchable(queryName: "AuthorMatchRequestsTablePaginationQuery")
      @argumentDefinitions(
        cursor: { type: "String" }
        first: { type: "Int", defaultValue: 50 }
        orderBy: { type: "String" }
        showEveryonesTags: { type: "Boolean", defaultValue: false }
      ) {
        requestedMatches(
          first: $first
          after: $cursor
          orderBy: $orderBy
          showEveryonesTags: $showEveryonesTags
        ) @connection(key: "AuthorMatchRequestsTable_user_requestedMatches") {
          edges {
            node {
              id
              started

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

              tags(showEveryonesTags: $showEveryonesTags) {
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
          }
        }
      }
    `,
    props.data,
  );

  type MatchType = NonNullable<
    NonNullable<
      NonNullable<
        AuthorMatchRequestsTable_user$data["requestedMatches"]
      >["edges"][number]
    >["node"]
  >;

  const [showEveryonesTags, setShowEveryonesTags] = useState(false);

  const [isPending, startTransition] = useTransition();

  const matchData = useMemo(
    () => getNodes<MatchType>(data?.requestedMatches),
    [data],
  );

  const columnHelper = createColumnHelper<MatchType>();

  const columns = useMemo(
    () => [
      columnHelper.accessor((row) => row.id, {
        id: "id",
        header: "ID",

        cell: (info) => {
          const matchId = getIDFromBase64(info.getValue(), "MatchType") || "";

          const href = reverseUrl("match", {
            pk: matchId,
          });

          const aria = `View match details for match ID ${matchId}`;

          return (
            <span className="flex justify-between">
              <Link
                className="font-semibold text-gray-200 truncate mr-2"
                to={href}
                role="cell"
                aria-label={aria}
                title={`${matchId}`}
              >
                {matchId}
              </Link>
            </span>
          );
        },

        meta: {
          priority: 1,
        },
      }),

      columnHelper.accessor((row) => row.participant1?.name || "", {
        id: "participant1",
        header: "Bot",

        cell: (info) => {
          const participant1 = info.row.original.participant1;

          const displayValue = hideSpoilers
            ? participant1?.name
            : formatWinnerName(
                info.row.original.result?.winner?.name,
                participant1?.name,
              );

          const label = participant1?.name || "";

          const botId = getIDFromBase64(participant1?.id, "BotType");

          const aria = `View bot profile for ${participant1?.name}, Bot`;

          return (
            <span className="flex justify-between">
              {botId ? (
                <Link
                  className="font-semibold text-gray-200 truncate mr-2"
                  to={reverseUrl("bot", {
                    pk: botId,
                  })}
                  role="cell"
                  aria-label={aria}
                  title={label}
                >
                  <span className="flex">
                    <RenderRace withoutText race={participant1?.playsRace} />

                    {displayValue || label}
                  </span>
                </Link>
              ) : (
                <span className="font-semibold text-gray-200 truncate mr-2">
                  <span className="flex">
                    <RenderRace withoutText race={participant1?.playsRace} />

                    {displayValue || label}
                  </span>
                </span>
              )}
            </span>
          );
        },

        meta: {
          priority: 1,
        },
      }),

      columnHelper.accessor((row) => row.participant2?.name || "", {
        id: "participant2",
        header: "Opponent",

        cell: (info) => {
          const participant2 = info.row.original.participant2;

          const displayValue = hideSpoilers
            ? participant2?.name
            : formatWinnerName(
                info.row.original.result?.winner?.name,
                participant2?.name,
              );

          const label = participant2?.name || "";

          const botId = getIDFromBase64(participant2?.id, "BotType");

          const aria = `View bot profile for ${participant2?.name}, Opponent`;

          return (
            <span className="flex justify-between">
              {botId ? (
                <Link
                  className="font-semibold text-gray-200 truncate mr-2"
                  to={reverseUrl("bot", {
                    pk: botId,
                  })}
                  role="cell"
                  aria-label={aria}
                  title={label}
                >
                  <span className="flex">
                    <RenderRace withoutText race={participant2?.playsRace} />

                    {displayValue || label}
                  </span>
                </Link>
              ) : (
                <span className="font-semibold text-gray-200 truncate mr-2">
                  <span className="flex">
                    <RenderRace withoutText race={participant2?.playsRace} />

                    {displayValue || label}
                  </span>
                </span>
              )}
            </span>
          );
        },

        meta: {
          priority: 1,
        },
      }),

      columnHelper.accessor((row) => row.map?.name ?? "", {
        id: "map",
        header: "Map",

        cell: (info) => {
          const downloadLink = info.row.original.map?.downloadLink;

          const name = info.getValue();

          return <DownloadMap downloadLink={downloadLink} name={name} />;
        },

        meta: {
          priority: 1,
        },
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

        meta: {
          priority: 1,
        },
      }),

      columnHelper.accessor((row) => row.result?.gameTimeFormatted ?? "", {
        id: "gameTime",
        header: "Duration",
        enableSorting: false,

        cell: (info) => info.getValue(),

        meta: {
          priority: 1,
        },

        size: 50,
      }),

      columnHelper.accessor((row) => row.started ?? "", {
        id: "started",
        header: "Started",

        cell: (info) => {
          const time = getDateTimeISOString(info.getValue());

          return time !== "" ? time : "In Queue";
        },

        meta: {
          priority: 1,
        },
      }),

      columnHelper.accessor((row) => row.result?.replayFile ?? "", {
        id: "replay",
        header: "Replay",
        enableSorting: false,

        cell: (info) => {
          if (!info.getValue()) {
            return null;
          }

          const href = `${info.getValue()}`;

          const matchId = getIDFromBase64(info.row.original.id, "MatchType");

          const aria = `Download replay file for Match ${matchId}`;

          return (
            <span className="flex justify-between">
              <Link
                className="font-semibold text-gray-200 truncate mr-2"
                to={href}
                role="cell"
                aria-label={aria}
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

        meta: {
          priority: 1,
        },

        size: 50,
      }),

      columnHelper.accessor((row) => row.tags ?? "", {
        id: "tags",
        header: "Tags",
        enableSorting: false,

        cell: (info) => {
          const nodes = getNodes(info.row.original.tags);

          return (
            <TagSummaryWithModal
              tagNodes={nodes}
              previewCount={1}
              title={`Tags - Match Id: ${getIDFromBase64(
                info.row.original.id,
                "MatchType",
              )}`}
            />
          );
        },

        meta: {
          priority: 1,
        },
      }),
    ],
    [columnHelper, hideSpoilers],
  );

  const { loadMoreRef } = useInfiniteScroll(() => loadNext(50), hasNext);

  const [sorting, setSorting] = useState<SortingState>([]);

  useEffect(() => {
    const sortingMap: Record<string, string> = {
      id: "id",
      participant1: "participant1__bot__name",
      participant2: "participant2__bot__name",
      result: "result__type",
      map: "map__name",
      started: "started",
      tags: "tags",
    };

    startTransition(() => {
      const sortString = parseSort(sortingMap, sorting);

      refetch(
        {
          orderBy: sortString,
          showEveryonesTags,
        },
        {
          fetchPolicy: "network-only",
        },
      );
    });
  }, [sorting, showEveryonesTags, refetch]);

  const table = useReactTable({
    data: matchData,
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

  const hasItems = matchData.length > 0;

  return (
    <div>
      <Suspense fallback={<LoadingDots />}>
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
                  <label
                    htmlFor="author-match-show-all-tags"
                    className="text-sm font-medium text-gray-300"
                  >
                    Show all tags
                  </label>

                  <SimpleToggle
                    enabled={showEveryonesTags}
                    onChange={() => {
                      setShowEveryonesTags((prev) => !prev);
                    }}
                  />
                </div>
              </div>
            }
          />
        ) : (
          <NoItemsInListMessage>
            <p>This author has not requested any matches.</p>
          </NoItemsInListMessage>
        )}
      </Suspense>

      {hasNext ? (
        <div className="flex justify-center mt-6" ref={loadMoreRef}>
          <LoadingMoreItems loadingMessage="Loading more match requests..." />
        </div>
      ) : !hasNext && hasItems ? (
        <div className="mt-8">
          <NoMoreItems />
        </div>
      ) : null}
    </div>
  );
}
