import { useEffect, useState } from "react";
import { fetchQuery, graphql } from "react-relay";
import RelayEnvironment from "@/_lib/RelayEnvironment.ts";
import { getNodes } from "@/_lib/relayHelpers.ts";
import {
  BotSearchListQuery,
  BotSearchListQuery$data,
} from "./__generated__/BotSearchListQuery.graphql";
import SearchList from "@/_components/_actions/SearchList";

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
  const [total, setTotal] = useState<number | null>(null);

  useEffect(() => {
    fetchQuery<BotSearchListQuery>(
      RelayEnvironment,
      graphql`
        query BotSearchListQuery($name: String) {
          bots(name: $name, first: 30) {
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
      { fetchPolicy: "store-or-network" }
    )
      .toPromise()
      .then((data) => {
        setOptions(getNodes(data?.bots));
        setTotal(data?.bots?.totalCount ?? null);
      });
  }, [query]);

  return (
    <SearchList
      value={value}
      setValue={(newValue) => setValue(newValue as BotType)}
      options={options}
      setQuery={setQuery}
      displayValue={(bot) => (bot as BotType)?.name}
      placeholder={total ? `Type to search ${total} agents...` : ""}
    />
  );
}
