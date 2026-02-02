import { graphql, usePaginationFragment } from "react-relay";
import {
  ColumnDef,
  ColumnSizingState,
  getCoreRowModel,
  useReactTable,
  VisibilityState,
} from "@tanstack/react-table";
import { useEffect, useMemo } from "react";
import { getNodes } from "@/_lib/relayHelpers";
import { BotResultsRow, ResultsFilters } from "./BotResultsTable";
import { flexRender } from "@tanstack/react-table";
import { BotResultsTbody_bot$key } from "./__generated__/BotResultsTbody_bot.graphql";
import { useInfiniteScroll } from "@/_components/_hooks/useInfiniteScroll";
import NoMoreItems from "@/_components/_display/NoMoreItems";
import TbodyLoadingSkeleton from "@/_components/_display/_skeletons/TableLoadingSkeleton";

export type TableState = {
  columnVisibility: VisibilityState;
  columnSizing: ColumnSizingState;
};

export type TableSetters = {
  setColumnVisibility: React.Dispatch<React.SetStateAction<VisibilityState>>;
  setColumnSizing: React.Dispatch<React.SetStateAction<ColumnSizingState>>;
};

export type BotResultsRefetchArgs = {
  filters: ResultsFilters;
  orderBy: string;
};

export function BotResultsTbody({
  fragmentRef,
  columns,
  state,
  onState,
  exposeRefetch,
  columnCount,
}: {
  fragmentRef: BotResultsTbody_bot$key;
  columns: ColumnDef<BotResultsRow, unknown>[];
  state: TableState;
  onState: TableSetters;
  exposeRefetch: (fn: (args: BotResultsRefetchArgs) => void) => void;
  columnCount: number;
}) {
  const { data, refetch, loadNext, hasNext } = usePaginationFragment(
    graphql`
      fragment BotResultsTbody_bot on BotType
      @refetchable(queryName: "BotResultsTablePaginationQuery")
      @argumentDefinitions(
        cursor: { type: "String" }
        first: { type: "Int", defaultValue: 50 }
        orderBy: { type: "String", defaultValue: "-id" }
        opponentId: { type: "String" }
        opponentPlaysRace: { type: "String" }
        result: { type: "String" }
        cause: { type: "String" }
        avgStepTimeMin: { type: "Decimal" }
        avgStepTimeMax: { type: "Decimal" }
        gameTimeMin: { type: "Decimal" }
        gameTimeMax: { type: "Decimal" }
        matchType: { type: "String" }
        mapName: { type: "String" }
        competitionId: { type: "String" }
        matchStartedAfter: { type: "DateTime" }
        matchStartedBefore: { type: "DateTime" }
        includeStarted: { type: "Boolean", defaultValue: false }
        includeQueued: { type: "Boolean", defaultValue: false }
        includeFinished: { type: "Boolean", defaultValue: true }
      ) {
        matchParticipations(
          first: $first
          after: $cursor
          orderBy: $orderBy
          opponentId: $opponentId
          opponentPlaysRace: $opponentPlaysRace
          result: $result
          cause: $cause
          avgStepTimeMin: $avgStepTimeMin
          avgStepTimeMax: $avgStepTimeMax
          gameTimeMax: $gameTimeMax
          gameTimeMin: $gameTimeMin
          matchType: $matchType
          mapName: $mapName
          competitionId: $competitionId
          matchStartedAfter: $matchStartedAfter
          matchStartedBefore: $matchStartedBefore
          includeStarted: $includeStarted
          includeQueued: $includeQueued
          includeFinished: $includeFinished
        ) @connection(key: "ResultsTable_node_matchParticipations") {
          edges {
            node {
              id
              result
              resultCause
              matchLog
              avgStepTime
              eloChange
              bot {
                id
                name
                playsRace {
                  name
                  label
                  id
                }
              }
              match {
                id
                started
                status
                participant1 {
                  name
                  id
                  playsRace {
                    name
                    label
                  }
                }
                participant2 {
                  name
                  id
                  playsRace {
                    name
                    label
                  }
                }
                map {
                  id
                  name
                }
                round {
                  competition {
                    id
                    name
                  }
                }
                result {
                  created
                  type
                  gameTimeFormatted
                  replayFile

                  participant1 {
                    eloChange
                    id
                    bot {
                      name
                      id
                    }
                    result
                  }
                  participant2 {
                    eloChange
                    id
                    bot {
                      name
                      id
                    }
                    result
                  }
                }
              }
            }
          }
        }
      }
    `,
    fragmentRef,
  );
  const { loadMoreRef } = useInfiniteScroll(() => loadNext(100), hasNext);
  useEffect(() => {
    exposeRefetch((args: BotResultsRefetchArgs) => {
      const f = args.filters;

      refetch({
        opponentId: f.opponentId,
        opponentPlaysRace: f.opponentPlaysRaceId,
        result: f.result?.toLowerCase(),
        cause: f.cause?.toLowerCase(),
        avgStepTimeMin: f.avgStepTimeMin,
        avgStepTimeMax: f.avgStepTimeMax,
        gameTimeMin: f.gameTimeMin,
        gameTimeMax: f.gameTimeMax,
        matchType: f.matchType?.toLowerCase(),
        mapName: f.mapName,
        competitionId: f.competitionId,
        matchStartedAfter: f.matchStartedAfter,
        matchStartedBefore: f.matchStartedBefore,
        includeStarted: f.includeStarted,
        includeQueued: f.includeQueued,
        includeFinished: f.includeFinished,
        orderBy: args.orderBy,
        first: 50,
      });
    });
  }, [exposeRefetch, refetch]);

  const rowsData = useMemo(() => getNodes(data?.matchParticipations), [data]);

  const bodyTable = useReactTable<BotResultsRow>({
    data: rowsData,
    columns,
    getCoreRowModel: getCoreRowModel(),
    enableColumnResizing: true,
    columnResizeMode: "onChange",
    manualSorting: true,
    state,
    onColumnVisibilityChange: onState.setColumnVisibility,
    onColumnSizingChange: onState.setColumnSizing,
  });
  const matchParticipationData = useMemo(
    () => getNodes<BotResultsRow>(data?.matchParticipations),
    [data],
  );
  const hasItems = matchParticipationData.length > 0;

  if (bodyTable.getRowModel().rows.length === 0) {
    return (
      <tbody>
        <tr>
          <td
            colSpan={bodyTable.getVisibleLeafColumns().length}
            className="p-6 text-center text-neutral-400"
          >
            No results
          </td>
        </tr>
      </tbody>
    );
  }

  return (
    <tbody>
      {bodyTable.getRowModel().rows.map((row) => (
        <tr
          key={row.id}
          className="even:bg-darken-4 odd:bg-darken hover:bg-darken-3 border-b border-gray-700"
        >
          {row.getVisibleCells().map((cell) => (
            <td
              key={cell.id}
              style={{ width: cell.column.getSize() }}
              className="p-3 text-white border-y border-darken-2 md:min-w-0 md:max-w-0"
            >
              <div className="w-full md:overflow-hidden md:text-ellipsis md:whitespace-nowrap">
                {flexRender(cell.column.columnDef.cell, cell.getContext())}
              </div>
            </td>
          ))}
        </tr>
      ))}
      {hasNext ? (
        <>
          <TbodyLoadingSkeleton colCount={columnCount} rowCount={24} />
          <div className="w-full" ref={loadMoreRef}></div>
        </>
      ) : !hasNext && hasItems ? (
        <div className="mt-8">
          <NoMoreItems />
        </div>
      ) : null}
    </tbody>
  );
}
