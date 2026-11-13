import { useMemo } from "react";
import { graphql, useFragment } from "react-relay";
import { getCoreRowModel, useReactTable } from "@tanstack/react-table";

import { TableContainer } from "@/_components/_actions/TableContainer";
import NoItemsInListMessage from "@/_components/_display/NoItemsInListMessage";
import {
  readResultRow,
  useResultColumns,
} from "@/_components/_display/resultsTable/resultColumns";
import { ArenaClientResults_arenaClient$key } from "./__generated__/ArenaClientResults_arenaClient.graphql";

interface ArenaClientResultsProps {
  arenaClient: ArenaClientResults_arenaClient$key;
}

export default function ArenaClientResults(props: ArenaClientResultsProps) {
  // Only the latest results, not a paginated list: paginating would count all
  // of a busy client's results on every load (see `recentResults` in the API).
  const { recentResults } = useFragment(
    graphql`
      fragment ArenaClientResults_arenaClient on ArenaClientType {
        recentResults {
          ...resultColumns_result
        }
      }
    `,
    props.arenaClient,
  );

  const rows = useMemo(() => recentResults.map(readResultRow), [recentResults]);
  const columns = useResultColumns();

  const table = useReactTable({
    data: rows,
    columns,
    getCoreRowModel: getCoreRowModel(),
    enableColumnResizing: true,
    columnResizeMode: "onChange",
  });

  if (rows.length === 0) {
    return (
      <NoItemsInListMessage>
        <p>This client hasn't played any matches yet.</p>
      </NoItemsInListMessage>
    );
  }

  return <TableContainer table={table} loading={false} />;
}
