import { startTransition, useState } from "react";
import { graphql, usePaginationFragment } from "react-relay";

import { getNodes } from "@/_lib/relayHelpers.ts";
import SearchList from "@/_components/_actions/SearchList";

import { useInfiniteScroll } from "@/_components/_hooks/useInfiniteScroll";
import { useDebouncedSearch } from "@/_components/_hooks/useDebouncedSearch";
import {
  CompetitionSearchList$data,
  CompetitionSearchList$key,
} from "./__generated__/CompetitionSearchList.graphql";

export type CompetitionType = NonNullable<
  NonNullable<
    NonNullable<CompetitionSearchList$data["competitions"]>["edges"][number]
  >["node"]
>;

interface CompetitionSearchListProps {
  value: CompetitionType | null;
  setValue: (map: CompetitionType | null) => void;
  relayRootQuery: CompetitionSearchList$key;
}

export default function CompetitionSearchList({
  value,
  setValue,
  relayRootQuery,
}: CompetitionSearchListProps) {
  const [query, setQuery] = useState("");

  const { data, loadNext, hasNext, refetch } = usePaginationFragment(
    graphql`
      fragment CompetitionSearchList on Query
      @argumentDefinitions(
        cursor: { type: "String" }
        name: { type: "String" }
        first: { type: "Int", defaultValue: 50 }
      )
      @refetchable(queryName: "CompetitionSearchListPaginationQuery") {
        competitions(first: $first, after: $cursor, name: $name)
          @connection(key: "RequestMatchModal_query_competitions") {
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
      setValue={(newValue) => setValue(newValue as CompetitionType)}
      options={getNodes(data?.competitions)}
      setQuery={setQuery}
      displayValue={(map) => (map as CompetitionType)?.name}
      placeholder={"Type to search competitions..."}
      hasNext={hasNext}
      loadMoreRef={loadMoreRef}
    />
  );
}
