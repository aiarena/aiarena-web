import { graphql, usePaginationFragment } from "react-relay";
import {
  createColumnHelper,
  getCoreRowModel,
  SortingState,
  useReactTable,
} from "@tanstack/react-table";
import {
  MatchRequestsTable_viewer$data,
  MatchRequestsTable_viewer$key,
} from "./__generated__/MatchRequestsTable_viewer.graphql";
import { getIDFromBase64, getNodes } from "@/_lib/relayHelpers";

import LoadingDots from "../_display/LoadingDots";
import { useInfiniteScroll } from "../_hooks/useInfiniteScroll";
import { Suspense, useEffect, useMemo, useState } from "react";
import { getDateTimeISOString } from "@/_lib/dateUtils";

import { getMatchResultParsed } from "@/_lib/parseMatchResult";
import { TableContainer } from "./TableContainer";
import { parseSort, withAtag } from "@/_lib/tanstack_utils";

interface MatchRequestsTableProps {
  viewer: MatchRequestsTable_viewer$key;
  loading: boolean;
}

export default function MatchRequestsTable(props: MatchRequestsTableProps) {
  const { data, loadNext, hasNext, refetch } = usePaginationFragment(
    graphql`
      fragment MatchRequestsTable_viewer on Viewer
      @argumentDefinitions(
        cursor: { type: "String" }
        first: { type: "Int", defaultValue: 50 }
        orderBy: { type: "String" }
      )
      @refetchable(queryName: "MatchRequestsTablePaginationQuery") {
        user {
          id
        }
        requestedMatches(first: $first, after: $cursor, orderBy: $orderBy)
          @connection(key: "UserMatchRequestsSection_viewer_requestedMatches") {
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

  type MatchType = NonNullable<
    NonNullable<
      NonNullable<
        MatchRequestsTable_viewer$data["requestedMatches"]
      >["edges"][number]
    >["node"]
  >;

  const [onlyMyTags, setOnlyMyTags] = useState(true);

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
        header: "Agent 1",
        cell: (info) =>
          withAtag(
            info.getValue() || "",
            `/bots/${getIDFromBase64(info.row.original.participant1?.id, "BotType")}`,
            `View bot profile for ${info.getValue()}, Agent 1`
          ),
        meta: { priority: 1 },
      }),
      columnHelper.accessor((row) => row.participant2?.name || "", {
        id: "participant2",
        header: "Agent 2",
        cell: (info) =>
          withAtag(
            info.getValue() || "",
            `/bots/${getIDFromBase64(info.row.original.participant2?.id, "BotType")}`,
            `View bot profile for ${info.getValue()}, Agent 2`
          ),
        meta: { priority: 1 },
      }),
      columnHelper.accessor((row) => row.map?.name ?? "", {
        id: "map",
        header: "Map",
        cell: (info) => info.getValue(),
        meta: { priority: 1 },
      }),
      columnHelper.accessor(
        (row) =>
          getNodes(row.tags)
            .filter((tag) =>
              onlyMyTags ? tag.user.id == data?.user?.id : true
            )
            .map((tag) => tag.tag)
            .join(", ") ?? "",
        {
          id: "tags",
          header: "Tags",
          cell: (info) => info.getValue(),
          meta: { priority: 1 },
        }
      ),
      columnHelper.accessor((row) => row.started ?? "A", {
        id: "started",
        header: "Started",
        cell: (info) => {
          const getTime = getDateTimeISOString(info.getValue());
          return getTime !== "" ? getTime : "In Queue";
        },
        meta: { priority: 1 },
      }),

      columnHelper.accessor((row) => row.result?.type || "A", {
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

    const sortString = parseSort(sortingMap, sorting);
    refetch({ orderBy: sortString });
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

  return (
    <div>
      <div className="mb-4 flex flex-wrap gap-4 text-white">
        <label key={"set_my_tags"} className="flex items-center space-x-2">
          <input
            type="checkbox"
            checked={onlyMyTags}
            onChange={() => setOnlyMyTags(!onlyMyTags)}
            className="accent-customGreen"
          />
          <span>Hide Tags by other authors</span>
        </label>
      </div>

      <Suspense fallback={<LoadingDots />}>
        <TableContainer table={table} loading={props.loading} />
      </Suspense>
      {hasNext && (
        <div className="flex justify-center mt-8" ref={loadMoreRef}>
          <LoadingDots />
        </div>
      )}
    </div>
  );
}
