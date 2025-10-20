import React, { useState, useRef, useEffect, ReactElement } from "react";
import { ChevronDownIcon } from "@heroicons/react/20/solid";
import clsx from "clsx";
import { DropdownButtonProps } from "./DropdownButton";

interface DropdownProps {
  title: string;
  isLoading?: boolean;
  children:
    | ReactElement<DropdownButtonProps>
    | ReactElement<DropdownButtonProps>[];
}

export default function Dropdown({
  title,
  children,
  isLoading = false,
}: DropdownProps) {
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

  // Injects closeDropdown into children
  const enhancedChildren = React.Children.map(children, (child) => {
    if (React.isValidElement(child)) {
      return React.cloneElement(child, {
        closeDropdown: () => setIsOpen(false),
      });
    }
    return child;
  });

  return (
    <div className="relative inline-block text-left" ref={dropdownRef}>
      <div>
        <button
          onClick={() => setIsOpen((prev) => !prev)}
          className={clsx(
            "inline-flex",
            "w-full",
            "justify-center",
            "gap-x-1.5",
            "rounded-md",
            "px-3",
            "py-3",
            "font-semibold",
            "bg-neutral-900",
            "shadow-xs",
            "border",
            "ring-1",
            "ring-inset",
            "ring-gray-700",
            "focus:outline-none",
            {
              "border-customGreen animate-border-fade-in-out": isLoading,
              "border-neutral-600": !isLoading,
              "focus:ring-customGreen focus:ring-2": true,
            },
          )}
        >
          {title}
          <ChevronDownIcon
            aria-hidden="true"
            className={clsx("-mr-1", "size-5", "text-gray-400")}
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
            "border-customGreen",
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
          <div className="py-1 flex flex-col">{enhancedChildren}</div>
        </div>
      )}
    </div>
  );
}
