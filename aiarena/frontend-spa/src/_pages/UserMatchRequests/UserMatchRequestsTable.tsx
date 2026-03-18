import { graphql, usePaginationFragment } from "react-relay";
import {
  createColumnHelper,
  getCoreRowModel,
  SortingState,
  useReactTable,
  VisibilityState,
} from "@tanstack/react-table";

import { getIDFromBase64, getNodes } from "@/_lib/relayHelpers";

import { Suspense, useEffect, useMemo, useState, useTransition } from "react";
import { getDateTimeISOString } from "@/_lib/dateUtils";

import { getMatchResultParsed } from "@/_lib/parseMatchResult";

import { parseSort } from "@/_lib/tanstack_utils";

import {
  UserMatchRequestsTable_viewer$data,
  UserMatchRequestsTable_viewer$key,
} from "./__generated__/UserMatchRequestsTable_viewer.graphql";
import NoItemsInListMessage from "@/_components/_display/NoItemsInListMessage";
import { formatWinnerName } from "@/_components/_display/formatWinnerName";
import { useRegisterConnectionID } from "@/_components/_hooks/useRegisterRelayConnectionID";
import { CONNECTION_KEYS } from "@/_components/_contexts/RelayConnectionIDContext/RelayConnectionIDKeys";
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
import TagSummaryWithModal from "../Rework/Bot/BotResultsTable/TagSummaryModal";
import DownloadMap from "@/_components/_display/DownloadMap";

interface UserMatchRequestsTableProps {
  viewer: UserMatchRequestsTable_viewer$key;
}

export default function UserMatchRequestsTable(
  props: UserMatchRequestsTableProps,
) {
  const [columnVisibility, setColumnVisibility] =
    useStateWithLocalStorage<VisibilityState>(
      "UserMatchRequests_UserMatchRequestsTable_ColumnVisibility",
      {},
    );

  const { data, loadNext, hasNext, refetch } = usePaginationFragment(
    graphql`
      fragment UserMatchRequestsTable_viewer on Viewer
      @refetchable(queryName: "UserMatchRequestsTablePaginationQuery")
      @argumentDefinitions(
        cursor: { type: "String" }
        first: { type: "Int", defaultValue: 50 }
        orderBy: { type: "String" }
        showEveryonesTags: { type: "Boolean", defaultValue: false }
      ) {
        user {
          id
        }
        requestedMatches(
          first: $first
          after: $cursor
          orderBy: $orderBy
          showEveryonesTags: $showEveryonesTags
        ) @connection(key: "UserMatchRequestsSection_viewer_requestedMatches") {
          __id
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
          }
        }
      }
    `,
    props.viewer,
  );

  useRegisterConnectionID(
    CONNECTION_KEYS.UserMatchRequestsConnection,
    data?.requestedMatches?.__id,
  );

  type MatchType = NonNullable<
    NonNullable<
      NonNullable<
        UserMatchRequestsTable_viewer$data["requestedMatches"]
      >["edges"][number]
    >["node"]
  >;

  const [hideOtherAuthorsTags, setHideOtherAuthorsTags] = useState(false);
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
          const label = getIDFromBase64(info.getValue(), "MatchType") || "";
          const href = `/matches/${getIDFromBase64(info.getValue(), "MatchType")}`;
          const aria = `View match details for match ID ${info.getValue()}`;

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

      columnHelper.accessor((row) => row.participant1?.name || "", {
        id: "participant1",
        header: "Bot",
        cell: (info) => {
          const participant1 = info.row.original.participant1;
          const display_value = formatWinnerName(
            info.row.original.result?.winner?.name,
            participant1?.name,
          );

          const label = participant1?.name || "";
          const href = `/bots/${getIDFromBase64(info.row.original.participant1?.id, "BotType")}`;
          const aria = `View bot profile for ${participant1?.name}, Bot`;
          const children = display_value;

          return (
            <span className="flex justify-between">
              <Link
                className="font-semibold text-gray-200 truncate mr-2"
                to={href}
                role="cell"
                aria-label={aria}
                title={`${label}`}
              >
                <span className="flex">
                  <RenderRace withoutText race={participant1?.playsRace} />
                  {children ? children : label}
                </span>
              </Link>
            </span>
          );
        },
        meta: { priority: 1 },
      }),
      columnHelper.accessor((row) => row.participant2?.name || "", {
        id: "participant2",
        header: "Opponent",
        cell: (info) => {
          const participant2 = info.row.original.participant2;

          const display_value = formatWinnerName(
            info.row.original.result?.winner?.name,
            info.row.original.participant2?.name,
          );

          const label = participant2?.name || "";
          const href = `/bots/${getIDFromBase64(participant2?.id, "BotType")}`;
          const aria = `View bot profile for ${participant2?.name}, Opponent`;
          const children = display_value;

          return (
            <span className="flex justify-between">
              <Link
                className="font-semibold text-gray-200 truncate mr-2"
                to={href}
                role="cell"
                aria-label={aria}
                title={`${label}`}
              >
                <span className="flex">
                  <RenderRace withoutText race={participant2?.playsRace} />
                  {children ? children : label}
                </span>
              </Link>
            </span>
          );
        },

        meta: { priority: 1 },
      }),
      columnHelper.accessor((row) => row.map?.name ?? "", {
        id: "map",
        header: "Map",
        cell: (info) => {
          const downloadLink = info.row.original.map.downloadLink;
          const name = info.getValue();
          return <DownloadMap downloadLink={downloadLink} name={name} />;
        },
        meta: { priority: 1 },
      }),

      columnHelper.accessor((row) => row.result?.type, {
        id: "result",
        header: "Result",
        cell: (info) => {
          const getResult = getMatchResultParsed(
            info.getValue(),
            info.row.original.participant1?.name,
            info.row.original.participant2?.name,
          );
          return getResult != "" ? getResult : "In Queue";
        },

        meta: { priority: 1 },
      }),
      columnHelper.accessor((row) => row.result?.gameTimeFormatted ?? "", {
        id: "gameTime",
        header: "Duration",
        cell: (info) => {
          return info.getValue();
        },
        meta: { priority: 1 },
        size: 50,
      }),

      columnHelper.accessor((row) => row.started ?? "", {
        id: "started",
        header: "Started",
        cell: (info) => {
          const getTime = getDateTimeISOString(info.getValue());
          return getTime !== "" ? getTime : "In Queue";
        },
        meta: { priority: 1 },
      }),
      columnHelper.accessor((row) => row.result?.replayFile ?? "", {
        id: "replay",
        header: "Replay",
        enableSorting: false,
        cell: (info) => {
          if (info.getValue()) {
            const label = "Download";
            const href = `${info.getValue()}`;
            const aria = `Download replay file for Match ${info.row.original.id}`;
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
              title={`Tags - Match Id: ${getIDFromBase64(info.row.original.id, "MatchType")}`}
            />
          );
        },
        meta: { priority: 1 },
      }),
    ],
    [columnHelper],
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
          showEveryonesTags: hideOtherAuthorsTags,
        },
        {
          fetchPolicy: "network-only",
        },
      );
    });
  }, [sorting, hideOtherAuthorsTags, refetch]);

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
                className="flex gap-4  items-center"
                role="group"
                aria-label="Bot filtering controls"
              >
                <div className="flex items-center gap-2">
                  <label
                    htmlFor="downloadable-toggle"
                    className="text-sm font-medium text-gray-300"
                  >
                    Show all tags
                  </label>
                  <SimpleToggle
                    enabled={hideOtherAuthorsTags}
                    onChange={() => {
                      setHideOtherAuthorsTags((prev) => !prev);
                    }}
                  />
                </div>
              </div>
            }
          />
        ) : (
          <NoItemsInListMessage>
            <p>Request your first match, and it will show up here.</p>
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
