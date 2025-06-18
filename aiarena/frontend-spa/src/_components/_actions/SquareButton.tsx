import React, { MouseEventHandler } from "react";
import { useNavigate } from "react-router";
import clsx from "clsx";

interface SquareButtonProps {
  href?: string;
  text?: string;
  className?: string;
  outerClassName?: string;
  onClick?: MouseEventHandler<HTMLButtonElement>;
  isLoading?: boolean;
  disabled?: boolean;
  children?: React.ReactNode;
  textColor?: "bright" | "dim";
}

export default function SquareButton({
  href,
  text,
  className = "",
  outerClassName,
  onClick,
  isLoading,
  disabled,
  children,
  textColor = "bright",
}: SquareButtonProps) {
  const navigate = useNavigate();

  const handleClick: React.MouseEventHandler<HTMLButtonElement> = (event) => {
    if (onClick) {
      onClick(event);
    } else if (href) {
      navigate(href);
    }
  };

  return (
    <>
      <style>{`
        @keyframes highlight {
          0% {
            border-color: transparent;
            border-bottom-color: var(--color-customGreen);
          }
          25% {
            border-left-color: var(--color-customGreen);
          }
          50% {
            border-top-color: var(--color-customGreen);
          }
          75% {
            border-right-color: var(--color-customGreen);
          }
          100% {
            border-color: transparent;
            border-bottom-color: var(--color-customGreen);
          }
        }
        .animate-highlight {
          position: absolute;
          top: -4px;
          left: -4px;
          width: calc(100% + 8px);
          height: calc(100% + 8px);
          border: 2px solid transparent;
          border-radius: 7px;
          animation: highlight 1s linear infinite;
          animation-delay: 0.15s;
        }
      `}</style>
      <div className={clsx("relative inline-block", outerClassName)}>
        <button
          onClick={handleClick}
          className={clsx(
            "flex justify-center items-center w-full shadow-sm shadow-black border-2 font-semibold py-1 px-2 rounded-sm transition duration-300 ease-in-out transform backdrop-blur-sm",
            {
              "text-white": textColor === "bright",
              "text-gray-200": textColor === "dim",
              "hover:shadow-customGreen border-customGreen bg-darken-2 hover:border-customGreen hover:bg-transparent":
                !disabled,
              "bg-darken border-gray-700 hover:bg-darken hover:border-gray-700 cursor-not-allowed":
                disabled,
            },
            className
          )}
          disabled={isLoading || disabled}
        >
          {children}
          {text}
        </button>
        {isLoading && <div className="animate-highlight"></div>}
      </div>
    </>
  );
}
