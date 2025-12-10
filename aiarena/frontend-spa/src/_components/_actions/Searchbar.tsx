import clsx from "clsx";
import { useEffect, useState } from "react";

interface SearchbarProps {
  placeholder: string;
  onChange: (value: string) => void;
  value: string;
  isLoading?: boolean;
  debounceMs?: number;
  classNames?: string;
}

export default function Searchbar({
  placeholder,
  onChange,
  value,
  isLoading = false,
  debounceMs = 300,
  classNames,
}: SearchbarProps) {
  const [localValue, setLocalValue] = useState(value);

  useEffect(() => {
    setLocalValue(value);
  }, [value]);

  useEffect(() => {
    const timer = setTimeout(() => {
      if (localValue !== value) {
        onChange(localValue);
      }
    }, debounceMs);

    return () => clearTimeout(timer);
  }, [localValue, value, onChange, debounceMs]);

  return (
    <div className="max-w-[40em]">
      <input
        type="text"
        value={localValue}
        onChange={(e) => setLocalValue(e.target.value)}
        placeholder={placeholder}
        className={clsx(
          "p-3",
          "m-0",
          "border",
          "rounded",
          "shadow-sm",
          "focus:outline-none",
          "focus:ring-2",
          "focus:ring-customGreen",
          "bg-darken-2",
          "text-white",
          "placeholder-neutral-400",
          classNames && classNames,
          {
            "border-customGreen animate-border-fade-in-out": isLoading,
            "border-neutral-600": !isLoading,
          }
        )}
      />
    </div>
  );
}
