import { Menu, MenuButton, MenuItems } from "@headlessui/react";
import { ChevronDownIcon } from "@heroicons/react/20/solid";
import { ReactNode } from "react";
interface DropdownTWProps {
  title: string;
  children: ReactNode;
}
export default function DropdownTW({ title, children }: DropdownTWProps) {
  return (
    <Menu as="div" className="relative inline-block text-left">
      <div>
        <MenuButton className="inline-flex w-full justify-center gap-x-1.5 rounded-md  px-3 py-3 font-semibold bg-gray-900  shadow-xs ring-1 ring-gray-700 focus:outline-none focus:ring-customGreen focus:ring-2 ring-inset">
          {title}
          <ChevronDownIcon
            aria-hidden="true"
            className="-mr-1 size-5 text-gray-400"
          />
        </MenuButton>
      </div>

      <MenuItems
        modal={false}
        transition
        className="absolute left-0 right-auto mt-2 max-w-screen-sm w-56 border-2 border-customGreen rounded-md bg-gray-900 shadow-lg ring-1 ring-black/5 focus:outline-none overflow-x-auto"
      >
        <div className="py-1">{children}</div>
      </MenuItems>
    </Menu>
  );
}
