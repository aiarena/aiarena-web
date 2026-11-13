import { useMemo, useState } from "react";
import { graphql, useFragment } from "react-relay";
import { Link } from "react-router";
import {
  createColumnHelper,
  getCoreRowModel,
  getSortedRowModel,
  SortingState,
  useReactTable,
} from "@tanstack/react-table";

import { TableContainer } from "@/_components/_actions/TableContainer";
import { getIDFromBase64, getNodes } from "@/_lib/relayHelpers";
import { reverseUrl } from "@/_lib/reverseUrl";
import {
  ArenaClientsTable_node$data,
  ArenaClientsTable_node$key,
} from "./__generated__/ArenaClientsTable_node.graphql";

interface ArenaClientsTableProps {
  data: ArenaClientsTable_node$key;
}

type ArenaClient = NonNullable<
  NonNullable<
    NonNullable<ArenaClientsTable_node$data["arenaClients"]>["edges"][number]
  >["node"]
>;

const columnHelper = createColumnHelper<ArenaClient>();

export default function ArenaClientsTable(props: ArenaClientsTableProps) {
  // Only active clients are listed, and there are only ever a handful, so one
  // page holds them all; sorting happens client-side.
  const data = useFragment(
    graphql`
      fragment ArenaClientsTable_node on Query {
        arenaClients(first: 100) {
          edges {
            node {
              id
              username
              owner {
                id
                username
              }
              matches1h
              matches24h
            }
          }
        }
      }
    `,
    props.data,
  );

  const clients = useMemo(
    () => getNodes<ArenaClient>(data.arenaClients),
    [data],
  );

  const columns = useMemo(
    () => [
      columnHelper.accessor("username", {
        id: "name",
        header: "Name",
        cell: (info) => (
          <Link
            className="font-semibold text-gray-200 truncate"
            to={reverseUrl("arenaclient", {
              pk: getIDFromBase64(info.row.original.id, "ArenaClientType"),
            })}
            title={info.getValue()}
          >
            {info.getValue()}
          </Link>
        ),
        meta: { priority: 1 },
      }),
      columnHelper.accessor((row) => row.owner.username, {
        id: "owner",
        header: "Owner",
        cell: (info) => (
          <Link
            className="font-semibold text-gray-200 truncate"
            to={reverseUrl("author", {
              pk: getIDFromBase64(info.row.original.owner.id, "UserType"),
            })}
            title={info.getValue()}
          >
            {info.getValue()}
          </Link>
        ),
        meta: { priority: 1 },
      }),
      columnHelper.accessor("matches1h", {
        id: "matches1h",
        header: "Matches (1h)",
        meta: { priority: 1 },
      }),
      columnHelper.accessor("matches24h", {
        id: "matches24h",
        header: "Matches (24h)",
        meta: { priority: 1 },
      }),
    ],
    [],
  );

  const [sorting, setSorting] = useState<SortingState>([]);

  const table = useReactTable({
    data: clients,
    columns,
    getCoreRowModel: getCoreRowModel(),
    getSortedRowModel: getSortedRowModel(),
    enableColumnResizing: true,
    columnResizeMode: "onChange",
    state: { sorting },
    onSortingChange: setSorting,
  });

  return <TableContainer table={table} loading={false} />;
}
