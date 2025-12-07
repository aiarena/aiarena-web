import { graphql, usePaginationFragment } from "react-relay";
import {
  createColumnHelper,
  getCoreRowModel,
  SortingState,
  useReactTable,
} from "@tanstack/react-table";

import { getIDFromBase64, getNodes } from "@/_lib/relayHelpers";

import React, {
  Suspense,
  useEffect,
  useMemo,
  useState,
  startTransition,
} from "react";

import { parseSort, withAtag } from "@/_lib/tanstack_utils";

import NoMoreItems from "@/_components/_display/NoMoreItems";
import LoadingMoreItems from "@/_components/_display/LoadingMoreItems";
import { TableContainer } from "@/_components/_actions/TableContainer";
import LoadingDots from "@/_components/_display/LoadingDots";
import { useInfiniteScroll } from "@/_components/_hooks/useInfiniteScroll";
import {
  BotsTable_node$data,
  BotsTable_node$key,
} from "./__generated__/BotsTable_node.graphql";

interface BotsTableProps {
  data: BotsTable_node$key;
  searchBarValue: string;
  onlyDownloadable: boolean;
  appendHeader?: React.ReactNode;
}

export default function BotsTable(props: BotsTableProps) {
  const { data, loadNext, hasNext, refetch } = usePaginationFragment(
    graphql`
      fragment BotsTable_node on Query
      @refetchable(queryName: "BotsTablePaginationQuery")
      @argumentDefinitions(
        cursor: { type: "String" }
        first: { type: "Int", defaultValue: 50 }
        orderBy: { type: "String" }
        name: { type: "String" }
        botZipPubliclyDownloadable: { type: "Boolean" }
      ) {
        bots(
          first: $first
          after: $cursor
          orderBy: $orderBy
          name: $name
          botZipPubliclyDownloadable: $botZipPubliclyDownloadable
        ) @connection(key: "BotsTable_node_bots") {
          edges {
            node {
              id
              name
              type
              playsRace {
                name
                label
                id
              }
              user {
                id
                username
                type
              }
            }
          }
        }
      }
    `,
    props.data
  );

  type BotType = NonNullable<
    NonNullable<
      NonNullable<BotsTable_node$data["bots"]>["edges"][number]
    >["node"]
  >;

  const botData = useMemo(() => getNodes<BotType>(data?.bots), [data]);

  const columnHelper = createColumnHelper<BotType>();

  const columns = useMemo(
    () => [
      columnHelper.accessor((row) => row.name || "", {
        id: "name",
        header: "Name",
        enableSorting: false,
        cell: (info) =>
          withAtag(
            info.getValue(),
            `/bots/${getIDFromBase64(info.row.original.id, "BotType")}`,
            `View bot profile for ${info.getValue()}`
          ),
        meta: { priority: 1 },
      }),
      columnHelper.accessor((row) => row.user.username || "", {
        id: "author",
        header: "Author",
        enableSorting: false,

        cell: (info) =>
          withAtag(
            info.getValue(),
            `/authors/${getIDFromBase64(info.row.original.user.id, "UserType")}`,
            `View author profile for ${info.getValue()}`
          ),
        meta: { priority: 1 },
      }),
      columnHelper.accessor((row) => row.playsRace.name ?? "", {
        id: "race",
        header: "Race",
        enableSorting: false,
        cell: (info) => info.getValue() || "N/A",
        meta: { priority: 1 },
      }),
      columnHelper.accessor((row) => row.type ?? "", {
        id: "type",
        header: "Type",
        enableSorting: false,
        cell: (info) => info.getValue(),
        meta: { priority: 1 },
      }),
    ],
    [columnHelper]
  );

  const { loadMoreRef } = useInfiniteScroll(() => loadNext(50), hasNext);
  const [sorting, setSorting] = useState<SortingState>([]);

  useEffect(() => {
    const sortingMap: Record<string, string> = {
      name: "name",
      author: "user__username",
      race: "plays_race",
      type: "type",
    };
    startTransition(() => {
      const sortString = parseSort(sortingMap, sorting);
      refetch({
        orderBy: sortString,
        name: props.searchBarValue,
        botZipPubliclyDownloadable: props.onlyDownloadable,
      });
    });
  }, [sorting, props.searchBarValue, props.onlyDownloadable, refetch]);

  const table = useReactTable({
    data: botData,
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

  const hasItems = botData.length > 0;

  return (
    <div>
      <Suspense fallback={<LoadingDots />}>
        <TableContainer
          table={table}
          loading={false}
          appendHeader={props.appendHeader}
        />
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
