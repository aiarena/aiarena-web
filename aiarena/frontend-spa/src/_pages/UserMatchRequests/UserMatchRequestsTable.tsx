import { graphql, usePaginationFragment } from "react-relay";
import {
  createColumnHelper,
  getCoreRowModel,
  SortingState,
  useReactTable,
} from "@tanstack/react-table";

import { getIDFromBase64, getNodes } from "@/_lib/relayHelpers";

import { Suspense, useEffect, useMemo, useState, useTransition } from "react";
import { getDateTimeISOString } from "@/_lib/dateUtils";

import { getMatchResultParsed } from "@/_lib/parseMatchResult";

import { parseSort, withAtag } from "@/_lib/tanstack_utils";

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

interface UserMatchRequestsTableProps {
  viewer: UserMatchRequestsTable_viewer$key;
}

export default function UserMatchRequestsTable(
  props: UserMatchRequestsTableProps
) {
  const { data, loadNext, hasNext, refetch } = usePaginationFragment(
    graphql`
      fragment UserMatchRequestsTable_viewer on Viewer
      @argumentDefinitions(
        cursor: { type: "String" }
        first: { type: "Int", defaultValue: 50 }
        orderBy: { type: "String" }
      )
      @refetchable(queryName: "UserMatchRequestsTablePaginationQuery") {
        user {
          id
        }
        requestedMatches(first: $first, after: $cursor, orderBy: $orderBy)
          @connection(key: "UserMatchRequestsSection_viewer_requestedMatches") {
          __id
          edges {
            node {
              id
              started
              participant1 {
                id
                name
              }
              participant2 {
                id
                name
              }
              result {
                type
                winner {
                  name
                }
              }
              tags {
                edges {
                  cursor
                  node {
                    id
                    tag
                    user {
                      id
                    }
                  }
                }
              }
              map {
                name
              }
            }
          }
        }
      }
    `,
    props.viewer
  );

  useRegisterConnectionID(
    CONNECTION_KEYS.UserMatchRequestsConnection,
    data?.requestedMatches?.__id
  );

  type MatchType = NonNullable<
    NonNullable<
      NonNullable<
        UserMatchRequestsTable_viewer$data["requestedMatches"]
      >["edges"][number]
    >["node"]
  >;

  const [onlyMyTags, setOnlyMyTags] = useState(true);
  const [isPending, startTransition] = useTransition();
  const matchData = useMemo(
    () => getNodes<MatchType>(data?.requestedMatches),
    [data]
  );

  const columnHelper = createColumnHelper<MatchType>();

  const columns = useMemo(
    () => [
      columnHelper.accessor((row) => row.id, {
        id: "id",
        header: "ID",
        cell: (info) =>
          withAtag(
            getIDFromBase64(info.getValue(), "MatchType") || "",
            `/matches/${getIDFromBase64(info.getValue(), "MatchType")}`,
            `View match details for match ID ${info.getValue()}`
          ),

        meta: { priority: 1 },
      }),
      columnHelper.accessor((row) => row.participant1?.name || "", {
        id: "participant1",
        header: "Bot",
        cell: (info) => {
          const participant1 = info.row.original.participant1;
          const display_value = formatWinnerName(
            info.row.original.result?.winner?.name,
            participant1?.name
          );

          return withAtag(
            participant1?.name || "",
            `/bots/${getIDFromBase64(info.row.original.participant1?.id, "BotType")}`,
            `View bot profile for ${participant1?.name}, Bot`,
            display_value
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
            info.row.original.participant2?.name
          );

          return withAtag(
            participant2?.name || "",
            `/bots/${getIDFromBase64(participant2?.id, "BotType")}`,
            `View bot profile for ${participant2?.name}, Opponent`,
            display_value
          );
        },

        meta: { priority: 1 },
      }),
      columnHelper.accessor((row) => row.map?.name ?? "", {
        id: "map",
        header: "Map",
        cell: (info) => info.getValue(),
        meta: { priority: 1 },
      }),
      columnHelper.accessor((row) => getNodes(row.tags) ?? "", {
        id: "tags",
        header: "Tags",
        cell: (info) => {
          const tags = info.getValue();
          const filtered = tags.filter((tag) =>
            onlyMyTags ? tag.user.id === data?.user?.id : true
          );
          return filtered.map((tag) => tag?.tag).join(", ");
        },
        meta: { priority: 1 },
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

      columnHelper.accessor((row) => row.result?.type, {
        id: "result",
        header: "Result",
        cell: (info) => {
          const getResult = getMatchResultParsed(
            info.getValue(),
            info.row.original.participant1?.name,
            info.row.original.participant2?.name
          );
          return getResult != "" ? getResult : "In Queue";
        },

        meta: { priority: 1 },
      }),
    ],
    [columnHelper, data?.user?.id, onlyMyTags]
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
      refetch({ orderBy: sortString });
    });
  }, [sorting, refetch]);

  const table = useReactTable({
    data: matchData,
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
                    Hide Tags by other authors
                  </label>
                  <SimpleToggle
                    enabled={onlyMyTags}
                    onChange={() => setOnlyMyTags(!onlyMyTags)}
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
