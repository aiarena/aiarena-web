import {
  Combobox,
  ComboboxButton,
  ComboboxInput,
  ComboboxOption,
  ComboboxOptions,
} from "@headlessui/react";
import clsx from "clsx";
import { ChevronDownIcon } from "@heroicons/react/20/solid";

interface SearchListOption {
  id: string;
  [x: string]: unknown;
}

interface SearchListProps {
  value: SearchListOption | null;
  setValue: (newValue: SearchListOption) => void;
  options: SearchListOption[];
  setQuery: (newValue: string) => void;
  displayValue: (option: SearchListOption) => string;
  placeholder: string;
}

export default function SearchList({
  value,
  setValue,
  options,
  setQuery,
  displayValue,
  placeholder,
}: SearchListProps) {
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
          placeholder={placeholder}
          displayValue={displayValue}
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
        modal={false}
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
        {options.map((bot: SearchListOption) => (
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
            {displayValue(bot)}
          </ComboboxOption>
        ))}
      </ComboboxOptions>
    </Combobox>
  );
}
