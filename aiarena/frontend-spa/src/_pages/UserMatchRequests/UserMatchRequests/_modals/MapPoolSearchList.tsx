import { startTransition, useState } from "react";
import { graphql, usePaginationFragment } from "react-relay";

import { getNodes } from "@/_lib/relayHelpers.ts";
import SearchList from "@/_components/_actions/SearchList";

import { useDebouncedSearch } from "@/_components/_hooks/useDebouncedSearch";
import { useInfiniteScroll } from "@/_components/_hooks/useInfiniteScroll";
import {
  MapPoolSearchList$data,
  MapPoolSearchList$key,
} from "./__generated__/MapPoolSearchList.graphql";

export type MapPoolType = NonNullable<
  NonNullable<
    NonNullable<MapPoolSearchList$data["mapPools"]>["edges"][number]
  >["node"]
>;

interface MapPoolSearchListProps {
  value: MapPoolType | null;
  setValue: (mapPool: MapPoolType | null) => void;
  relayRootQuery: MapPoolSearchList$key;
}

export default function MapPoolSearchList({
  value,
  setValue,
  relayRootQuery,
}: MapPoolSearchListProps) {
  const [query, setQuery] = useState("");

  const { data, loadNext, hasNext, refetch } = usePaginationFragment(
    graphql`
      fragment MapPoolSearchList on Query
      @argumentDefinitions(
        cursor: { type: "String" }
        name: { type: "String" }
        first: { type: "Int", defaultValue: 50 }
      )
      @refetchable(queryName: "MapPoolSearchListPaginationQuery") {
        mapPools(first: $first, after: $cursor, name: $name)
          @connection(key: "RequestMatchModal_query_mapPools") {
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
      setValue={(newValue) => setValue(newValue as MapPoolType)}
      options={getNodes(data.mapPools)}
      setQuery={setQuery}
      displayValue={(mapPool) => (mapPool as MapPoolType)?.name}
      placeholder={"Type to search map pools..."}
      hasNext={hasNext}
      loadMoreRef={loadMoreRef}
    />
  );
}
