import { MenuItem } from "@headlessui/react";
import clsx from "clsx";

export interface DropdownMenuItemTWProps {
  onClick: () => void;
  title: string;
  closeDropdown?: () => void;
}

export default function DropdownMenuItemTW({
  onClick,
  title,
}: DropdownMenuItemTWProps) {
  return (
    <MenuItem>
      <button
        className={clsx(
          "w-full",
          "flex justify-between items-center",
          "px-3 py-2",
          "text-left",
          "hover:bg-slate-600",
          "transition"
        )}
        onClick={() => onClick()}
      >
        <span>{title}</span>
        <span>{">"}</span>
      </button>
    </MenuItem>
  );
}
