import { Switch } from "@headlessui/react";

type SimpleToggleProps = {
  enabled: boolean;
  onChange: (value: boolean) => void;
};

export default function SimpleToggle({ enabled, onChange }: SimpleToggleProps) {
  return (
    <Switch
      checked={enabled}
      onChange={onChange}
      className="group relative inline-flex h-6 w-11 shrink-0 cursor-pointer rounded-full border-2 border-transparent bg-gray-600 transition-colors duration-200 ease-in-out focus:ring-2 focus:ring-customGreen focus:ring-offset-2 focus:outline-hidden data-checked:bg-customGreen"
    >
      <span className="sr-only">Use setting</span>
      <span
        aria-hidden="true"
        className="pointer-events-none inline-block size-5 transform rounded-full bg-white shadow-sm ring-0 transition duration-200 ease-in-out group-data-checked:translate-x-5"
      />
    </Switch>
  );
}
