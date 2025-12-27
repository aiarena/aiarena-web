import { graphql, usePaginationFragment } from "react-relay";
import {
  createColumnHelper,
  getCoreRowModel,
  useReactTable,
} from "@tanstack/react-table";

import { getIDFromBase64, getNodes } from "@/_lib/relayHelpers";
import clsx from "clsx";

import { Suspense, useMemo, useState, useTransition } from "react";
import { getDateTimeISOString } from "@/_lib/dateUtils";

import { getMatchResultParsed } from "@/_lib/parseMatchResult";

import { withAtag } from "@/_lib/tanstack_utils";

import NoItemsInListMessage from "@/_components/_display/NoItemsInListMessage";
import NoMoreItems from "@/_components/_display/NoMoreItems";
import LoadingMoreItems from "@/_components/_display/LoadingMoreItems";
import { TableContainer } from "@/_components/_actions/TableContainer";
import LoadingDots from "@/_components/_display/LoadingDots";
import { useInfiniteScroll } from "@/_components/_hooks/useInfiniteScroll";
import {
  ResultsTable_node$data,
  ResultsTable_node$key,
} from "./__generated__/ResultsTable_node.graphql";
import { formatWinnerName } from "@/_components/_display/formatWinnerName";
import WatchYourGamesButton from "@/_components/_actions/WatchYourGamesButton";
import WatchGamesModal from "@/_pages/UserMatchRequests/UserMatchRequests/_modals/WatchGamesModal";
import { ArrowDownCircleIcon } from "@heroicons/react/24/outline";

interface ResultsTableProps {
  data: ResultsTable_node$key;
}

export default function ResultsTable(props: ResultsTableProps) {
  const { data, loadNext, hasNext } = usePaginationFragment(
    graphql`
      fragment ResultsTable_node on Query
      @refetchable(queryName: "ResultsTablePaginationQuery")
      @argumentDefinitions(
        cursor: { type: "String" }
        first: { type: "Int", defaultValue: 50 }
      ) {
        results(first: $first, after: $cursor)
          @connection(key: "ResultsTable_node_results") {
          edges {
            node {
              created
              gameSteps
              id
              participant2 {
                bot {
                  id
                  name
                }
                eloChange
              }
              replayFile
              winner {
                id
              }
              type
              participant1 {
                bot {
                  id
                  name
                }
                eloChange
              }
              winner {
                name
              }
              started
              gameTimeFormatted
            }
          }
        }
      }
    `,
    props.data
  );

  type ResultType = NonNullable<
    NonNullable<
      NonNullable<ResultsTable_node$data["results"]>["edges"][number]
    >["node"]
  >;
  const [isWatchGamesModalOpen, setIsWatchGamesModalOpen] = useState(false);

  const [isPending] = useTransition();
  const matchData = useMemo(() => getNodes<ResultType>(data?.results), [data]);

  const columnHelper = createColumnHelper<ResultType>();

  const columns = useMemo(
    () => [
      columnHelper.accessor((row) => row.id, {
        id: "id",
        header: "ID",
        enableSorting: false,
        cell: (info) =>
          withAtag(
            getIDFromBase64(info.getValue(), "ResultType") || "",
            `/matches/${getIDFromBase64(info.getValue(), "ResultType")}`,
            `View match details for Result ID ${info.getValue()}`
          ),

        meta: { priority: 1 },
      }),
      columnHelper.accessor((row) => row.participant1?.bot.name || "", {
        id: "participant1",
        header: "Bot",
        enableSorting: false,
        cell: (info) => {
          const participant1 = info.row.original.participant1;
          const display_value = formatWinnerName(
            info.row.original.winner?.name,
            participant1?.bot.name
          );

          return withAtag(
            participant1?.bot.name || "",
            `/bots/${getIDFromBase64(info.row.original.participant1?.bot.id, "BotType")}`,
            `View bot profile for ${participant1?.bot.name}, Bot`,
            display_value,
            <span
              className={clsx({
                "text-red-400":
                  participant1?.eloChange && participant1?.eloChange < 0,
              })}
            >
              {participant1?.eloChange}
            </span>
          );
        },
        meta: { priority: 1 },
      }),

      columnHelper.accessor((row) => row.participant2?.bot.name || "", {
        id: "participant2",
        header: "Opponent",
        enableSorting: false,
        cell: (info) => {
          const participant2 = info.row.original.participant2;

          const display_value = formatWinnerName(
            info.row.original?.winner?.name,
            info.row.original.participant2?.bot.name
          );

          return withAtag(
            participant2?.bot.name || "",
            `/bots/${getIDFromBase64(participant2?.bot.id, "BotType")}`,
            `View bot profile for ${participant2?.bot.name}, Opponent`,
            display_value,
            <span
              className={clsx({
                "text-red-400":
                  participant2?.eloChange && participant2?.eloChange < 0,
              })}
            >
              {participant2?.eloChange}
            </span>
          );
        },

        meta: { priority: 1 },
      }),
      columnHelper.accessor((row) => row.type ?? "", {
        id: "type",
        header: "Result",
        enableSorting: false,
        cell: (info) => {
          const getResult = getMatchResultParsed(
            info.getValue(),
            info.row.original.participant1?.bot.name,
            info.row.original.participant2?.bot.name
          );
          return getResult != "" ? getResult : "In Queue";
        },
        meta: { priority: 1 },
      }),
      columnHelper.accessor((row) => row.gameTimeFormatted ?? "", {
        id: "gameTimeFormatted",
        header: "Duration",
        enableSorting: false,
        cell: (info) => info.getValue(),
        meta: { priority: 1 },
      }),

      columnHelper.accessor((row) => row.started ?? "", {
        id: "started",
        header: "Started",
        enableSorting: false,
        cell: (info) => {
          const getTime = getDateTimeISOString(info.getValue());
          return getTime !== "" ? getTime : "In Queue";
        },
        meta: { priority: 1 },
      }),

      columnHelper.accessor((row) => row.replayFile || "", {
        id: "replayFile",
        header: "Replay",
        enableSorting: false,
        cell: (info) => {
          const replayFile = info.row.original.replayFile;

          return withAtag(
            "Download",
            `/bots/${replayFile}`,
            `Get Replay for ${getIDFromBase64(info.row.original.id, "ResultType")}`,
            <span className="flex items-center gap-1">
              <ArrowDownCircleIcon height={18} /> Replay
            </span>
          );
        },

        meta: { priority: 1 },
      }),
    ],
    [columnHelper]
  );

  const { loadMoreRef } = useInfiniteScroll(() => loadNext(50), hasNext);

  const table = useReactTable({
    data: matchData,
    columns,
    getCoreRowModel: getCoreRowModel(),
    enableColumnResizing: true,
    columnResizeMode: "onChange",
    manualSorting: true,
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
              <WatchYourGamesButton
                onClick={() => setIsWatchGamesModalOpen(true)}
              >
                <span>Watch Replays on Twitch</span>
              </WatchYourGamesButton>
            }
          />
        ) : (
          <NoItemsInListMessage>
            <p>No Results meet the criteria...</p>
          </NoItemsInListMessage>
        )}
      </Suspense>

      {hasNext ? (
        <div className="flex justify-center mt-6" ref={loadMoreRef}>
          <LoadingMoreItems loadingMessage="Loading more results..." />
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
