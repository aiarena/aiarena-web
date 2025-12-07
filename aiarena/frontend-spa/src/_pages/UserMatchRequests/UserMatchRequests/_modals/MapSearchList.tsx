import { startTransition, useState } from "react";
import { graphql, usePaginationFragment } from "react-relay";

import { getNodes } from "@/_lib/relayHelpers.ts";
import SearchList from "@/_components/_actions/SearchList";

import { useInfiniteScroll } from "@/_components/_hooks/useInfiniteScroll";
import { useDebouncedSearch } from "@/_components/_hooks/useDebouncedSearch";
import {
  MapSearchList$data,
  MapSearchList$key,
} from "./__generated__/MapSearchList.graphql";

export type MapType = NonNullable<
  NonNullable<NonNullable<MapSearchList$data["maps"]>["edges"][number]>["node"]
>;

interface MapSearchListProps {
  value: MapType | null;
  setValue: (map: MapType | null) => void;
  relayRootQuery: MapSearchList$key;
}

export default function MapSearchList({
  value,
  setValue,
  relayRootQuery,
}: MapSearchListProps) {
  const [query, setQuery] = useState("");

  const { data, loadNext, hasNext, refetch } = usePaginationFragment(
    graphql`
      fragment MapSearchList on Query
      @argumentDefinitions(
        cursor: { type: "String" }
        name: { type: "String" }
        first: { type: "Int", defaultValue: 50 }
      )
      @refetchable(queryName: "MapSearchListPaginationQuery") {
        maps(first: $first, after: $cursor, name: $name)
          @connection(key: "RequestMatchModal_query_maps") {
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
      setValue={(newValue) => setValue(newValue as MapType)}
      options={getNodes(data?.maps)}
      setQuery={setQuery}
      displayValue={(map) => (map as MapType)?.name}
      placeholder={"Type to search maps..."}
      hasNext={hasNext}
      loadMoreRef={loadMoreRef}
    />
  );
}
