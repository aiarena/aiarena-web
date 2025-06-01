import { useEffect, useState } from "react";
import { fetchQuery, graphql } from "react-relay";
import RelayEnvironment from "@/_lib/RelayEnvironment.ts";
import { getNodes } from "@/_lib/relayHelpers.ts";
import SearchList from "@/_components/_sections/_modals/SearchList.tsx";
import {
  MapPoolSearchListQuery,
  MapPoolSearchListQuery$data,
} from "./__generated__/MapPoolSearchListQuery.graphql";

export type MapPoolType = NonNullable<
  NonNullable<
    NonNullable<MapPoolSearchListQuery$data["mapPools"]>["edges"][number]
  >["node"]
>;

interface MapPoolSearchListProps {
  value: MapPoolType | null;
  setValue: (mapPool: MapPoolType) => void;
}

export default function MapPoolSearchList({
  value,
  setValue,
}: MapPoolSearchListProps) {
  const [query, setQuery] = useState("");
  const [options, setOptions] = useState<MapPoolType[]>([]);
  const [total, setTotal] = useState<number | null>(null);

  useEffect(() => {
    fetchQuery<MapPoolSearchListQuery>(
      RelayEnvironment,
      graphql`
        query MapPoolSearchListQuery($name: String) {
          mapPools(name: $name, first: 10) {
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
      { name: query },
      { fetchPolicy: "store-or-network" },
    )
      .toPromise()
      .then((data) => {
        setOptions(getNodes(data?.mapPools));
        setTotal(data?.mapPools?.totalCount ?? null);
      });
  }, [query]);

  return (
    <SearchList
      value={value}
      setValue={(newValue) => setValue(newValue as MapPoolType)}
      options={options}
      setQuery={setQuery}
      displayValue={(mapPool) => (mapPool as MapPoolType)?.name}
      placeholder={total ? `Type to search ${total} map pools...` : ""}
    />
  );
}
