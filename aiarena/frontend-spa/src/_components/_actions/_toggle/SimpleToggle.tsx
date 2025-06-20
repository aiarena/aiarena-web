import { Switch } from "@headlessui/react";
import clsx from "clsx";

type SimpleToggleProps = {
  enabled: boolean;
  onChange: (value: boolean) => void;
  disabled?: boolean;
};

export default function SimpleToggle({
  enabled,
  onChange,
  disabled = false,
}: SimpleToggleProps) {
  return (
    <Switch
      checked={enabled}
      onChange={onChange}
      disabled={disabled}
      className={clsx(
        "group relative inline-flex h-6 w-11 shrink-0 rounded-full border-2",
        "bg-gray-600 transition-colors duration-200 ease-in-out",
        "focus:ring-2 focus:ring-customGreen focus:ring-offset-2 focus:outline-hidden",
        "data-checked:bg-customGreen-dark",
        enabled ? "border-customGreen" : "border-neutral-500",
        disabled ? "opacity-50 cursor-not-allowed" : "cursor-pointer"
      )}
    >
      <span className="sr-only">Use setting</span>
      <span
        aria-hidden="true"
        className={clsx(
          "pointer-events-none inline-block size-5 transform rounded-full",
          "bg-white shadow-sm ring-0 transition duration-200 ease-in-out",
          "group-data-checked:translate-x-5"
        )}
      />
    </Switch>
  );
}
