import Modal from "@/_components/_actions/Modal";
import { graphql, usePaginationFragment } from "react-relay";
import {
  CompetitionRoundsModal_competition$data,
  CompetitionRoundsModal_competition$key,
} from "./__generated__/CompetitionRoundsModal_competition.graphql";
import { Suspense, useMemo } from "react";
import { getIDFromBase64, getNodes } from "@/_lib/relayHelpers";
import {
  createColumnHelper,
  getCoreRowModel,
  useReactTable,
  VisibilityState,
} from "@tanstack/react-table";
import { useInfiniteScroll } from "@/_components/_hooks/useInfiniteScroll";
import LoadingDots from "@/_components/_display/LoadingDots";
import { TableContainer } from "@/_components/_actions/TableContainer";
import LoadingMoreItems from "@/_components/_display/LoadingMoreItems";
import NoMoreItems from "@/_components/_display/NoMoreItems";
import { getDateTimeISOString } from "@/_lib/dateUtils";
import { Link } from "react-router";
import useStateWithLocalStorage from "@/_components/_hooks/useStateWithLocalStorage";

interface CompetitionRoundsModalProps {
  competition: CompetitionRoundsModal_competition$key;
  noItemsMessage?: string;
  isOpen: boolean;
  onClose: () => void;
}

export default function CompetitionRoundsModal(
  props: CompetitionRoundsModalProps,
) {
  const [columnVisibility, setColumnVisibility] =
    useStateWithLocalStorage<VisibilityState>(
      "Competition_CompetitionRoundsModal_ColumnVisibility",
      {},
    );
  const { data, loadNext, hasNext } = usePaginationFragment(
    graphql`
      fragment CompetitionRoundsModal_competition on CompetitionType
      @refetchable(queryName: "CompetitionRoundsModalPaginationQuery")
      @argumentDefinitions(
        cursor: { type: "String" }
        first: { type: "Int", defaultValue: 10 }
      ) {
        name
        rounds(first: $first, after: $cursor)
          @connection(key: "CompetitionRoundsModal_competition_rounds") {
          edges {
            node {
              id
              number
              started
              finished
            }
          }
        }
      }
    `,
    props.competition,
  );

  type ParticipationType = NonNullable<
    NonNullable<
      NonNullable<
        CompetitionRoundsModal_competition$data["rounds"]
      >["edges"][number]
    >["node"]
  >;

  const competitionData = useMemo(
    () => getNodes<ParticipationType>(data?.rounds),
    [data],
  );

  const columnHelper = createColumnHelper<ParticipationType>();

  const columns = useMemo(
    () => [
      columnHelper.accessor((row) => row.number || "", {
        id: "id",
        header: "Id",
        enableSorting: false,
        cell: (info) => {
          const label = `Round ${info.getValue()}`;
          const href = `/rounds/${getIDFromBase64(info.row.original.id, "RoundsType")}`;
          const aria = `View round ${info.row.original.number}`;

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
      columnHelper.accessor((row) => row.started ?? "--", {
        id: "started",
        header: "Started",
        enableSorting: false,
        cell: (row) => getDateTimeISOString(row.getValue()) || "--",
        meta: { priority: 1 },
      }),
      columnHelper.accessor((row) => row.finished ?? "", {
        id: "finished",
        header: "Finished",
        enableSorting: false,
        cell: (row) => getDateTimeISOString(row.getValue()),
        meta: { priority: 1 },
      }),
    ],
    [columnHelper],
  );

  const { loadMoreRef } = useInfiniteScroll(() => loadNext(10), hasNext);

  const table = useReactTable({
    data: competitionData,
    columns,
    getCoreRowModel: getCoreRowModel(),
    enableColumnResizing: true,
    columnResizeMode: "onChange",
    manualSorting: true,
    initialState: {
      columnVisibility: columnVisibility ?? undefined,
    },
    state: {
      columnVisibility: columnVisibility ?? {},
    },
    onColumnVisibilityChange: (updater) => {
      const next =
        typeof updater === "function"
          ? updater(columnVisibility ?? {})
          : updater;
      setColumnVisibility(next);
    },
  });

  const hasItems = competitionData.length > 0;
  if (!props.isOpen) return null;
  return (
    <Modal
      onClose={props.onClose}
      isOpen={props.isOpen}
      title={`Rounds - ${data.name}`}
    >
      <div>
        <Suspense fallback={<LoadingDots />}>
          <TableContainer table={table} loading={false} />
        </Suspense>

        {hasNext ? (
          <div className="flex justify-center mt-6" ref={loadMoreRef}>
            <LoadingMoreItems loadingMessage="Loading more rounds..." />
          </div>
        ) : !hasNext && hasItems ? (
          <div className="mt-8">
            <NoMoreItems />
          </div>
        ) : null}
      </div>
    </Modal>
  );
}
