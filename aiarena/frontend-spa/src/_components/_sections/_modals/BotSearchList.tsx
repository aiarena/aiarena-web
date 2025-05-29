import { useEffect, useState } from "react";
import { fetchQuery, graphql } from "react-relay";
import RelayEnvironment from "@/_lib/RelayEnvironment.ts";
import { getNodes } from "@/_lib/relayHelpers.ts";
import {
  Combobox,
  ComboboxButton,
  ComboboxInput,
  ComboboxOption,
  ComboboxOptions,
} from "@headlessui/react";
import clsx from "clsx";
import { ChevronDownIcon } from "@heroicons/react/20/solid";
import {
  BotSearchListQuery,
  BotSearchListQuery$data,
} from "./__generated__/BotSearchListQuery.graphql";

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
    <Combobox value={value} onChange={setValue} immediate>
      <div className="relative">
        <ComboboxInput
          className={clsx(
            "bg-neutral-900",
            "border",
            "border-neutral-600",
            "pl-4",
            "pr-8",
            "py-2",
            "rounded-sm",
            "text-white",
            "w-full",
          )}
          placeholder="Search for bots..."
          displayValue={(bot: BotType) => bot?.name}
          onChange={(event) => setQuery(event.target.value)}
        />
        <ComboboxButton
          className={clsx("absolute", "inset-y-0", "right-0", "px-2.5")}
        >
          <ChevronDownIcon className={clsx("size-4 ", "fill-white")} />
        </ComboboxButton>
      </div>

      <ComboboxOptions
        anchor="bottom"
        transition
        className={clsx(
          "w-(--input-width)",
          "rounded-sm",
          "border",
          "border-white/5",
          "bg-neutral-900",
          "p-1",
          "[--anchor-gap:--spacing(1)]",
          "z-100",
        )}
      >
        {options.map((bot: BotType) => (
          <ComboboxOption
            key={bot.id}
            value={bot}
            className={clsx(
              "cursor-pointer",
              "rounded-sm",
              "px-4",
              "py-2",
              "select-none",
              "data-focus:bg-white/10",
              "text-white",
            )}
          >
            {bot.name}
          </ComboboxOption>
        ))}
      </ComboboxOptions>
    </Combobox>
  );
}
