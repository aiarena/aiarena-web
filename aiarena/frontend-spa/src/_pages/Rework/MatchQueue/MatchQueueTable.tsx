import { ReactNode, useMemo, useState } from "react";
import { graphql, useFragment } from "react-relay";
import { Link } from "react-router";
import {
  createColumnHelper,
  getCoreRowModel,
  getFilteredRowModel,
  getSortedRowModel,
  SortingState,
  useReactTable,
} from "@tanstack/react-table";

import { getIDFromBase64 } from "@/_lib/relayHelpers";
import { reverseUrl } from "@/_lib/reverseUrl";
import timeAgoShort from "@/_lib/timeAgoSort";
import { TableContainer } from "@/_components/_actions/TableContainer";
import {
  MatchQueueTable_matches$data,
  MatchQueueTable_matches$key,
} from "./__generated__/MatchQueueTable_matches.graphql";

interface MatchQueueTableProps {
  matches: MatchQueueTable_matches$key;
  /** Free text; a row is shown if any of its cells contains it. */
  filter: string;
  /** Section heading; hidden with the table when the filter leaves no rows. */
  title: ReactNode;
}

type QueuedMatch = MatchQueueTable_matches$data[number];

const columnHelper = createColumnHelper<QueuedMatch>();

function BotLink({ bot }: { bot: QueuedMatch["participant1"] }) {
  if (!bot) {
    return <span className="text-gray-400">?</span>;
  }
  return (
    <Link
      className="font-semibold text-gray-200 truncate"
      to={reverseUrl("bot", { pk: getIDFromBase64(bot.id, "BotType") })}
      title={bot.name}
    >
      {bot.name}
    </Link>
  );
}

export default function MatchQueueTable(props: MatchQueueTableProps) {
  const matches = useFragment(
    graphql`
      fragment MatchQueueTable_matches on MatchType @relay(plural: true) {
        id
        started
        map {
          name
        }
        participant1 {
          id
          name
        }
        participant2 {
          id
          name
        }
        assignedTo {
          id
          username
        }
      }
    `,
    props.matches,
  );

  const columns = useMemo(
    () => [
      columnHelper.accessor((row) => getIDFromBase64(row.id, "MatchType"), {
        id: "id",
        header: "Match ID",
        cell: (info) => (
          <Link
            className="font-semibold text-gray-200"
            to={reverseUrl("match", { pk: info.getValue() })}
          >
            {info.getValue()}
          </Link>
        ),
        meta: { priority: 1 },
      }),
      columnHelper.accessor((row) => row.participant1?.name ?? "", {
        id: "bot1",
        header: "Bot 1",
        cell: (info) => <BotLink bot={info.row.original.participant1} />,
        meta: { priority: 1 },
      }),
      columnHelper.accessor((row) => row.participant2?.name ?? "", {
        id: "bot2",
        header: "Bot 2",
        cell: (info) => <BotLink bot={info.row.original.participant2} />,
        meta: { priority: 1 },
      }),
      columnHelper.accessor((row) => row.map.name, {
        id: "map",
        header: "Map",
        meta: { priority: 1 },
      }),
      columnHelper.accessor((row) => row.started ?? "", {
        id: "started",
        header: "Started",
        cell: (info) =>
          info.getValue() ? (
            `${timeAgoShort(info.getValue())} ago`
          ) : (
            <span className="text-gray-400">Queued</span>
          ),
        meta: { priority: 1 },
      }),
      columnHelper.accessor((row) => row.assignedTo?.username ?? "", {
        id: "assignedTo",
        header: "Assigned to",
        cell: (info) => {
          const client = info.row.original.assignedTo;
          if (!client) {
            return <span className="text-gray-400">Queued</span>;
          }
          return (
            <Link
              className="font-semibold text-gray-200"
              to={reverseUrl("arenaclient", { pk: getIDFromBase64(client.id, "UserType") })}
            >
              {client.username}
            </Link>
          );
        },
        meta: { priority: 1 },
      }),
    ],
    [],
  );

  const [sorting, setSorting] = useState<SortingState>([]);

  // Relay hands back a read-only array; the table wants a mutable one.
  const rows = useMemo(() => [...matches], [matches]);

  const table = useReactTable({
    data: rows,
    columns,
    getCoreRowModel: getCoreRowModel(),
    getSortedRowModel: getSortedRowModel(),
    getFilteredRowModel: getFilteredRowModel(),
    globalFilterFn: "includesString",
    enableColumnResizing: true,
    columnResizeMode: "onChange",
    state: { sorting, globalFilter: props.filter },
    onSortingChange: setSorting,
  });

  // While filtering, drop sections with nothing left in them rather than
  // showing an empty table under every round.
  if (props.filter && table.getRowModel().rows.length === 0) {
    return null;
  }

  return (
    <div className="mb-8">
      <h3 className="mb-3 text-lg">{props.title}</h3>
      <TableContainer table={table} loading={false} />
    </div>
  );
}
