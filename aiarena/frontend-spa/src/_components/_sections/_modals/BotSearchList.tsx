import { useEffect, useState } from "react";
import { fetchQuery, graphql } from "react-relay";
import RelayEnvironment from "@/_lib/RelayEnvironment.ts";
import { getNodes } from "@/_lib/relayHelpers.ts";
import {
  BotSearchListQuery,
  BotSearchListQuery$data,
} from "./__generated__/BotSearchListQuery.graphql";
import SearchList from "@/_components/_sections/_modals/SearchList.tsx";

export type BotType = NonNullable<
  NonNullable<
    NonNullable<BotSearchListQuery$data["bots"]>["edges"][number]
  >["node"]
>;

interface BotSearchListProps {
  value: BotType | null;
  setValue: (bot: BotType) => void;
}

export default function BotSearchList({ value, setValue }: BotSearchListProps) {
  const [query, setQuery] = useState("");
  const [options, setOptions] = useState<BotType[]>([]);

  useEffect(() => {
    fetchQuery<BotSearchListQuery>(
      RelayEnvironment,
      graphql`
        query BotSearchListQuery($name: String) {
          bots(name: $name, first: 10) {
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
    )
      .toPromise()
      .then((data) => {
        setOptions(getNodes(data?.bots));
      });
  }, [query]);

  return (
    <SearchList
      value={value}
      setValue={(newValue) => setValue(newValue as BotType)}
      options={options}
      setQuery={setQuery}
      displayValue={(bot) => (bot as BotType)?.name}
      placeholder="Search bots..."
    />
  );
}
