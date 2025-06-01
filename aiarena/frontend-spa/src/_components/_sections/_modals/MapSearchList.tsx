import { useEffect, useState } from "react";
import { fetchQuery, graphql } from "react-relay";
import RelayEnvironment from "@/_lib/RelayEnvironment.ts";
import { getNodes } from "@/_lib/relayHelpers.ts";
import SearchList from "@/_components/_sections/_modals/SearchList.tsx";
import {
  MapSearchListQuery,
  MapSearchListQuery$data,
} from "./__generated__/MapSearchListQuery.graphql";

export type MapType = NonNullable<
  NonNullable<
    NonNullable<MapSearchListQuery$data["maps"]>["edges"][number]
  >["node"]
>;

interface MapSearchListProps {
  value: MapType | null;
  setValue: (map: MapType) => void;
}

export default function MapSearchList({ value, setValue }: MapSearchListProps) {
  const [query, setQuery] = useState("");
  const [options, setOptions] = useState<MapType[]>([]);
  const [total, setTotal] = useState<number | null>(null);

  useEffect(() => {
    fetchQuery<MapSearchListQuery>(
      RelayEnvironment,
      graphql`
        query MapSearchListQuery($name: String) {
          maps(name: $name, first: 10) {
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
        setOptions(getNodes(data?.maps));
        setTotal(data?.maps?.totalCount ?? null);
      });
  }, [query]);

  return (
    <SearchList
      value={value}
      setValue={(newValue) => setValue(newValue as MapType)}
      options={options}
      setQuery={setQuery}
      displayValue={(map) => (map as MapType)?.name}
      placeholder={total ? `Type to search ${total} maps...` : ""}
    />
  );
}
