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
  autocomplete?: "off" | "on";
  loadingFetchMore?: boolean;
  hasNext?: boolean;
  loadMoreRef?: (node: HTMLDivElement | null) => void;
}

export default function SearchList({
  value,
  setValue,
  options,
  setQuery,
  displayValue,
  placeholder,
  autocomplete = "off",
  hasNext,
  loadMoreRef,
}: SearchListProps) {
  const handleScroll = (e: React.UIEvent<HTMLDivElement>) => {
    const { scrollTop, scrollHeight, clientHeight } = e.currentTarget;
    const isInBottom10Percent =
      scrollTop >= (scrollHeight - clientHeight) * 0.9;

    if (isInBottom10Percent && hasNext && loadMoreRef) {
      loadMoreRef(e.currentTarget);
    }
  };

  return (
    <Combobox
      value={value}
      virtual={{
        options: options,
      }}
      onChange={setValue}
    >
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
            "w-full"
          )}
          placeholder={placeholder}
          displayValue={displayValue}
          onChange={(event) => setQuery(event.target.value)}
          autoComplete={autocomplete}
        />
        <ComboboxButton className="absolute inset-y-0 right-0 px-2.5">
          <ChevronDownIcon className="size-4 fill-white" />
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
          "combobox-options"
        )}
        onScroll={handleScroll}
      >
        {({ option: bot }) => (
          <ComboboxOption
            value={bot}
            className={clsx(
              "cursor-pointer",
              "rounded-sm",
              "px-4",
              "py-2",
              "select-none",
              "data-focus:bg-white/10",
              "text-white"
            )}
          >
            {bot.name}
          </ComboboxOption>
        )}
      </ComboboxOptions>
    </Combobox>
  );
}
