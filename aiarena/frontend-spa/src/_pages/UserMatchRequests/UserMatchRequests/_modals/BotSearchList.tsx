import { startTransition, useState } from "react";
import { graphql, usePaginationFragment } from "react-relay";

import { getNodes } from "@/_lib/relayHelpers.ts";

import { useDebouncedSearch } from "@/_components/_hooks/useDebouncedSearch";
import SearchList from "@/_components/_actions/SearchList";

import {
  BotSearchList$data,
  BotSearchList$key,
} from "./__generated__/BotSearchList.graphql";
import { useInfiniteScroll } from "@/_components/_hooks/useInfiniteScroll";

export type BotType = NonNullable<
  NonNullable<NonNullable<BotSearchList$data["bots"]>["edges"][number]>["node"]
>;

interface BotSearchListProps {
  value: BotType | null;
  setValue: (bot: BotType | null) => void;
  relayRootQuery: BotSearchList$key;
}

export default function BotSearchList({
  value,
  setValue,
  relayRootQuery,
}: BotSearchListProps) {
  const [query, setQuery] = useState("");

  const { data, loadNext, hasNext, refetch } = usePaginationFragment(
    graphql`
      fragment BotSearchList on Query
      @argumentDefinitions(
        cursor: { type: "String" }
        name: { type: "String" }
        first: { type: "Int", defaultValue: 50 }
      )
      @refetchable(queryName: "BotSearchListPaginationQuery") {
        bots(first: $first, after: $cursor, name: $name)
          @connection(key: "RequestMatchModal_query_bots") {
          totalCount
          edges {
            node {
              id
              name
            }
          }
        }
      }
    `,
    relayRootQuery
  );

  useDebouncedSearch(query, 500, (value) => {
    startTransition(() => {
      refetch({ name: value });
    });
  });

  const { loadMoreRef } = useInfiniteScroll(() => loadNext(100), hasNext);

  return (
    <SearchList
      value={value}
      setValue={(newValue) => setValue(newValue as BotType)}
      options={getNodes(data?.bots)}
      setQuery={setQuery}
      displayValue={(bot) => (bot as BotType)?.name || ""}
      placeholder={"Type to search bots..."}
      hasNext={hasNext}
      loadMoreRef={loadMoreRef}
    />
  );
}
