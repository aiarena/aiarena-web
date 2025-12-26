import { graphql, usePaginationFragment } from "react-relay";
import {
  createColumnHelper,
  getCoreRowModel,
  useReactTable,
} from "@tanstack/react-table";

import { getIDFromBase64, getNodes } from "@/_lib/relayHelpers";

import { Suspense, useMemo, useState, useTransition } from "react";
import { getDateTimeISOString } from "@/_lib/dateUtils";

import { withAtag } from "@/_lib/tanstack_utils";

import NoItemsInListMessage from "@/_components/_display/NoItemsInListMessage";
import NoMoreItems from "@/_components/_display/NoMoreItems";
import LoadingMoreItems from "@/_components/_display/LoadingMoreItems";
import { TableContainer } from "@/_components/_actions/TableContainer";
import LoadingDots from "@/_components/_display/LoadingDots";
import { useInfiniteScroll } from "@/_components/_hooks/useInfiniteScroll";

import WatchYourGamesButton from "@/_components/_actions/WatchYourGamesButton";
import WatchGamesModal from "@/_pages/UserMatchRequests/UserMatchRequests/_modals/WatchGamesModal";
import {
  RoundsTable_round$data,
  RoundsTable_round$key,
} from "./__generated__/RoundsTable_round.graphql";

interface RoundsTableProps {
  data: RoundsTable_round$key;
}

export default function RoundsTable(props: RoundsTableProps) {
  const { data, loadNext, hasNext } = usePaginationFragment(
    graphql`
      fragment RoundsTable_round on RoundsType
      @refetchable(queryName: "RoundsTablePaginationQuery")
      @argumentDefinitions(
        cursor: { type: "String" }
        first: { type: "Int", defaultValue: 25 }
      ) {
        id
        complete
        number
        matches(first: $first, after: $cursor)
          @connection(key: "RoundsTable_node_matches") {
          edges {
            node {
              status
              id
              started
              participant1 {
                id
                name
              }
              participant2 {
                name
                id
              }
              assignedTo {
                username
                id
              }
              result {
                created
                replayFile
              }
            }
          }
        }
      }
    `,
    props.data
  );

  type MatchType = NonNullable<
    NonNullable<
      NonNullable<RoundsTable_round$data["matches"]>["edges"][number]
    >["node"]
  >;
  const [isWatchGamesModalOpen, setIsWatchGamesModalOpen] = useState(false);
  const [isPending] = useTransition();
  const roundsData = useMemo(() => getNodes<MatchType>(data?.matches), [data]);

  const columnHelper = createColumnHelper<MatchType>();

  const columns = useMemo(
    () => [
      columnHelper.accessor((row) => row.id, {
        id: "id",
        header: "Match ID",
        enableSorting: false,
        cell: (info) =>
          withAtag(
            getIDFromBase64(info.getValue(), "MatchType") || "",
            `/matches/${getIDFromBase64(info.getValue(), "MatchType")}`,
            `View match details for Match ID ${info.getValue()}`
          ),

        meta: { priority: 1 },
      }),
      columnHelper.accessor((row) => row.participant1?.name || "", {
        id: "participant1",
        header: "Bot 1",
        enableSorting: false,
        cell: (info) => {
          return withAtag(
            info.getValue() || "",
            `/bots/${getIDFromBase64(info.row.original.participant1?.id, "BotType")}`,
            `View bot profile for ${info.getValue()}, Bot`
          );
        },
        meta: { priority: 1 },
      }),

      columnHelper.accessor((row) => row.participant2?.name || "", {
        id: "participant2",
        header: "Bot 2",
        enableSorting: false,
        cell: (info) => {
          return withAtag(
            info.getValue() || "",
            `/bots/${getIDFromBase64(info.row.original.participant2?.id, "BotType")}`,
            `View bot profile for ${info.getValue()}, Bot`
          );
        },
        meta: { priority: 1 },
      }),
      columnHelper.accessor((info) => info.started ?? "", {
        id: "started",
        header: "Started",
        enableSorting: false,
        cell: (info) => {
          const status = info.row.original.status;
          if (status === "Started" || status === "Finished") {
            return getDateTimeISOString(info.getValue());
          } else if (status === "Queued") {
            return "In Queue";
          } else {
            return "Error";
          }
        },
        meta: { priority: 1 },
      }),
      columnHelper.accessor((info) => info.result?.created ?? "", {
        id: "finished",
        header: "Finished",
        enableSorting: false,
        cell: (info) => {
          const status = info.row.original.status;
          if (status === "Finished") {
            return getDateTimeISOString(info.getValue());
          } else if (status === "Started") {
            return "In Progress...";
          } else if (status === "Queued") {
            return "In Queue";
          } else {
            return "Error";
          }
        },
        meta: { priority: 1 },
      }),

      columnHelper.accessor((row) => row.assignedTo || "", {
        id: "assignedTo",
        header: "Assigned to",
        enableSorting: false,
        cell: (info) => {
          const status = info.row.original.status;
          if (status === "Finished") {
            return withAtag(
              info.row.original.assignedTo?.username || "",
              `/bots/${getIDFromBase64(info.row.original.assignedTo?.id, "UserType")}`,
              `Visit userprofile for ${info.row.original.assignedTo?.id}`
            );
          } else if (status === "Started") {
            return "In Progress...";
          } else if (status === "Queued") {
            return "In Queue";
          } else {
            return "Error";
          }
        },

        meta: { priority: 1 },
      }),
    ],
    [columnHelper]
  );

  const { loadMoreRef } = useInfiniteScroll(() => loadNext(50), hasNext);

  const table = useReactTable({
    data: roundsData,
    columns,
    getCoreRowModel: getCoreRowModel(),
    enableColumnResizing: true,
    columnResizeMode: "onChange",
    manualSorting: true,
  });

  const hasItems = roundsData.length > 0;

  return (
    <div>
      <Suspense fallback={<LoadingDots />}>
        {hasItems ? (
          <TableContainer
            table={table}
            loading={isPending}
            appendHeader={
              <WatchYourGamesButton
                onClick={() => setIsWatchGamesModalOpen(true)}
              >
                <span>Watch Replays on Twitch</span>
              </WatchYourGamesButton>
            }
          />
        ) : (
          <NoItemsInListMessage>
            <p>No rounds meet the criteria...</p>
          </NoItemsInListMessage>
        )}
      </Suspense>

      {hasNext ? (
        <div className="flex justify-center mt-6" ref={loadMoreRef}>
          <LoadingMoreItems loadingMessage="Loading more matches..." />
        </div>
      ) : !hasNext && hasItems ? (
        <div className="mt-8">
          <NoMoreItems />
        </div>
      ) : null}
      <WatchGamesModal
        isOpen={isWatchGamesModalOpen}
        onClose={() => setIsWatchGamesModalOpen(false)}
      />
    </div>
  );
}
