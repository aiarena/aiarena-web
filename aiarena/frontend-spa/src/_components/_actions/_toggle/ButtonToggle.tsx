import React, { MouseEventHandler } from "react";
import clsx from "clsx";

interface ButtonToggleProps {
  text?: string;
  className?: string;
  outerClassName?: string;
  onClick?: MouseEventHandler<HTMLButtonElement>;
  isLoading?: boolean;
  active?: boolean;
  disabled?: boolean;
  children?: React.ReactNode;
}

export default function ButtonToggle({
  text,
  className = "",
  outerClassName,
  onClick,
  isLoading,
  active,
  disabled,
  children,
}: ButtonToggleProps) {
  const handleClick: React.MouseEventHandler<HTMLButtonElement> = (event) => {
    if (onClick) {
      onClick(event);
    }
  };

  return (
    <>
      <div className={clsx("relative inline-block", outerClassName)}>
        <button
          onClick={handleClick}
          className={clsx(
            "flex justify-center items-center w-full shadow-sm shadow-black border-2 font-semibold px-6 py-2  rounded-sm transition duration-100 ease-in-out transform backdrop-blur-sm",
            {
              "hover:shadow-customGreen  bg-neutral-900 hover:border-customGreen hover:bg-transparent":
                !disabled,
              "border-customGreen text-gray-200": active,
              "border-neutral-700 text-gray-400": !active,
              "bg-darken border-neutral-700  hover:bg-darken hover:border-neutral-600 cursor-not-allowed":
                disabled,
            },
            className,
          )}
          disabled={isLoading || disabled}
        >
          {children}
          {text}
        </button>
      </div>
    </>
  );
}
