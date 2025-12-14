import { graphql, usePaginationFragment } from "react-relay";
import {
  createColumnHelper,
  getCoreRowModel,
  useReactTable,
} from "@tanstack/react-table";

import { getIDFromBase64, getNodes } from "@/_lib/relayHelpers";

import { Suspense, useMemo } from "react";

import { withAtag } from "@/_lib/tanstack_utils";

import NoMoreItems from "@/_components/_display/NoMoreItems";
import LoadingMoreItems from "@/_components/_display/LoadingMoreItems";
import { TableContainer } from "@/_components/_actions/TableContainer";
import LoadingDots from "@/_components/_display/LoadingDots";
import { useInfiniteScroll } from "@/_components/_hooks/useInfiniteScroll";
import {
  AuthorBotsTable_user$data,
  AuthorBotsTable_user$key,
} from "./__generated__/AuthorBotsTable_user.graphql";
import RenderCodeLanguage from "@/_components/_display/RenderCodeLanguage";
import { RenderRace } from "@/_components/_display/RenderRace";

interface AuthorBotsTableProps {
  data: AuthorBotsTable_user$key;
}

export default function AuthorBotsTable(props: AuthorBotsTableProps) {
  const { data, loadNext, hasNext } = usePaginationFragment(
    graphql`
      fragment AuthorBotsTable_user on UserType
      @refetchable(queryName: "AuthorBotsTablePaginationQuery")
      @argumentDefinitions(
        cursor: { type: "String" }
        first: { type: "Int" }
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
        ) @connection(key: "AuthorBotsTable_node_bots") {
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
              trophies {
                edges {
                  node {
                    trophyIconImage
                  }
                }
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
      NonNullable<AuthorBotsTable_user$data["bots"]>["edges"][number]
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
      columnHelper.accessor((row) => getNodes(row.trophies).length ?? "", {
        id: "trophies",
        header: "Trophies",
        enableSorting: false,
        cell: (info) => info.getValue() || "0",
        meta: { priority: 1 },
      }),
      columnHelper.accessor((row) => row.playsRace.name ?? "", {
        id: "race",
        header: "Race",
        enableSorting: false,
        cell: (info) => <RenderRace race={info.row.original.playsRace} />,
        meta: { priority: 1 },
      }),
      columnHelper.accessor((row) => row.type ?? "", {
        id: "type",
        header: "Type",
        enableSorting: false,
        cell: (info) => <RenderCodeLanguage type={`${info.getValue()}`} />,
        meta: { priority: 1 },
      }),
    ],
    [columnHelper]
  );

  const { loadMoreRef } = useInfiniteScroll(() => loadNext(50), hasNext);

  const table = useReactTable({
    data: botData,
    columns,
    getCoreRowModel: getCoreRowModel(),
    enableColumnResizing: true,
    columnResizeMode: "onChange",
    manualSorting: true,
  });

  const hasItems = botData.length > 0;

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
