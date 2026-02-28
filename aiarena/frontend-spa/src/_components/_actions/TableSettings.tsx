import React, { useState, useRef, useEffect } from "react";

import clsx from "clsx";

import { ChartBarIcon } from "@heroicons/react/24/outline";
interface TableSettingsProps {
  children: React.ReactNode;
}

export default function TableSettings({ children }: TableSettingsProps) {
  const [isOpen, setIsOpen] = useState(false);
  const dropdownRef = useRef<HTMLDivElement>(null);

  // Close the dropdown if clicked outside
  useEffect(() => {
    function handleClickOutside(event: MouseEvent) {
      if (
        dropdownRef.current &&
        !dropdownRef.current.contains(event.target as Node)
      ) {
        setIsOpen(false);
      }
    }
    document.addEventListener("mousedown", handleClickOutside);
    return () => {
      document.removeEventListener("mousedown", handleClickOutside);
    };
  }, []);

  return (
    <div className="relative inline-block text-left " ref={dropdownRef}>
      <div>
        <button
          onClick={() => setIsOpen((prev) => !prev)}
          className={clsx(
            "inline-flex",
            "w-full",
            "justify-center",
            "rounded-md",
            "px-[1em]",
            "py-[0.6em]",
            "font-semibold",
            "bg-neutral-900",
            "shadow-xs",
            "border-2",

            "border-neutral-700",
            "hover:border-customGreen",
            {
              "focus:ring-customGreen focus:ring-2": true,
            },
          )}
        >
          <ChartBarIcon
            height={5}
            width={5}
            className={clsx(
              "-mr-1",
              "size-5",
              "text-gray-400",
              "rotate-90",
              "scale-x-[-1]",
            )}
          />
        </button>
      </div>

      {isOpen && (
        <div
          className={clsx(
            "absolute",
            "left-0",
            "right-auto",
            "mt-2",
            "max-w-screen-sm",
            "w-56",
            "border-2",
            "border-neutral-700",
            "rounded-md",
            "bg-neutral-900",
            "shadow-lg",
            "ring-1",
            "ring-neutral-800",
            "focus:outline-none",
            "transition",
            "duration-100",
            "ease-out",
            "z-45",
            "overflow-x-auto",
          )}
        >
          <div className="py-1 flex flex-col my-1">{children}</div>
        </div>
      )}
    </div>
  );
}
