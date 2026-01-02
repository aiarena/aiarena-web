import { graphql, usePaginationFragment } from "react-relay";
import { getIDFromBase64, getNodes } from "@/_lib/relayHelpers";
import {
  BotCompetitionsTable_bot$data,
  BotCompetitionsTable_bot$key,
} from "./__generated__/BotCompetitionsTable_bot.graphql";
import {
  ReactNode,
  startTransition,
  Suspense,
  useEffect,
  useMemo,
  useState,
} from "react";
import {
  createColumnHelper,
  getCoreRowModel,
  SortingState,
  useReactTable,
} from "@tanstack/react-table";
import { parseSort, withAtag } from "@/_lib/tanstack_utils";
import { useInfiniteScroll } from "@/_components/_hooks/useInfiniteScroll";
import LoadingDots from "@/_components/_display/LoadingDots";
import { TableContainer } from "@/_components/_actions/TableContainer";
import LoadingMoreItems from "@/_components/_display/LoadingMoreItems";
import NoMoreItems from "@/_components/_display/NoMoreItems";

interface BotCompetitionsTableProps {
  bot: BotCompetitionsTable_bot$key;
  appendHeader?: ReactNode;
  onlyActive?: boolean | undefined;
}

export default function BotCompetitionsTable(props: BotCompetitionsTableProps) {
  const { data, loadNext, hasNext, refetch } = usePaginationFragment(
    graphql`
      fragment BotCompetitionsTable_bot on BotType
      @refetchable(queryName: "BotCompetitionTablePaginationQuery")
      @argumentDefinitions(
        cursor: { type: "String" }
        first: { type: "Int", defaultValue: 50 }
        orderBy: { type: "String" }
        active: { type: "Boolean" }
      ) {
        competitionParticipations(
          first: $first
          after: $cursor
          orderBy: $orderBy
          active: $active
        )
          @connection(
            key: "BotCompetitionsTable_bot_competitionParticipations"
          ) {
          edges {
            node {
              id
              elo
              divisionNum
              active
              winPerc
              bot {
                name
              }
              competition {
                dateOpened
                dateClosed
                id
                name
              }
            }
          }
        }
      }
    `,
    props.bot
  );

  type ParticipationType = NonNullable<
    NonNullable<
      NonNullable<
        BotCompetitionsTable_bot$data["competitionParticipations"]
      >["edges"][number]
    >["node"]
  >;

  const competitionData = useMemo(
    () => getNodes<ParticipationType>(data?.competitionParticipations),
    [data]
  );

  const columnHelper = createColumnHelper<ParticipationType>();

  const columns = useMemo(
    () => [
      columnHelper.accessor((row) => row.competition.name || "", {
        id: "name",
        header: "Competition",
        enableSorting: false,
        cell: (info) =>
          withAtag(
            info.getValue(),
            `/competitions/${getIDFromBase64(info.row.original.competition.id, "CompetitionType")}`,
            `View competition ${info.row.original.competition.name}`
          ),
        meta: { priority: 1 },
        size: 350,
      }),
      columnHelper.accessor((row) => row.competition.dateOpened ?? "", {
        id: "dateOpened",
        header: "Opened",
        cell: (row) => new Date(row.getValue()).toLocaleDateString() || "--",
        meta: { priority: 1 },
      }),
      columnHelper.accessor((row) => row.competition.dateClosed ?? "", {
        id: "dateClosed",
        header: "Closed",
        enableSorting: false,
        cell: (row) => {
          if (row.getValue()) {
            return new Date(row.getValue()).toLocaleDateString() || "--";
          } else {
            return "--";
          }
        },
        meta: { priority: 1 },
      }),
      columnHelper.accessor((row) => row.divisionNum ?? "", {
        id: "divisionNum",
        header: "Division",
        enableSorting: false,
        cell: (info) => {
          const division = info.getValue();
          if (division !== 0) {
            return info.getValue();
          } else {
            return "";
          }
        },
        meta: { priority: 1 },
      }),
      columnHelper.accessor((row) => row.elo ?? "", {
        id: "elo",
        header: "ELO",
        enableSorting: false,
        cell: (info) => info.getValue(),
        meta: { priority: 1 },
      }),
      columnHelper.accessor((row) => row.winPerc ?? "", {
        id: "winPerc",
        header: "Win %",
        enableSorting: false,
        cell: (info) => {
          return `${Math.trunc(info.getValue())} %`;
        },
        meta: { priority: 1 },
      }),
      columnHelper.accessor((row) => row.id || "", {
        id: "stats",
        header: "Stats",
        enableSorting: false,
        cell: (info) => {
          return withAtag(
            "View Stats",
            `/competitions/stats/${getIDFromBase64(info.getValue(), "CompetitionParticipationType")}`,
            `View stats ${info.getValue()}`
          );
        },
        meta: { priority: 1 },
      }),
    ],
    [columnHelper]
  );

  const { loadMoreRef } = useInfiniteScroll(() => loadNext(50), hasNext);
  const [sorting, setSorting] = useState<SortingState>([]);
  useEffect(() => {
    const sortingMap: Record<string, string> = {
      dateOpened: "competition__date_opened",
    };
    startTransition(() => {
      const sortString = parseSort(sortingMap, sorting);
      refetch({
        orderBy: sortString,
        active: props.onlyActive == true ? true : undefined,
      });
    });
  }, [sorting, props.onlyActive, refetch]);

  const table = useReactTable({
    data: competitionData,
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

  const hasItems = competitionData.length > 0;

  return (
    <div>
      <Suspense fallback={<LoadingDots />}>
        <TableContainer
          table={table}
          loading={false}
          appendHeader={props.appendHeader}
          minHeight={20}
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
