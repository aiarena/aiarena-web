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
  color?: "green" | "orange" | "red";
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
  color = "green",
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
            border-bottom-color: var(--highlight-color);
          }
          25% {
            border-left-color: var(--highlight-color);
          }
          50% {
            border-top-color: var(--highlight-color);
          }
          75% {
            border-right-color: var(--highlight-color);
          }
          100% {
            border-color: transparent;
            border-bottom-color: var(--highlight-color);
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

        .highlight-green {
          --highlight-color: var(--color-customGreen);
        }

        .highlight-orange {
          --highlight-color: #f97316; /* Tailwind orange-500 */
        }

        .highlight-red {
          --highlight-color: #ef4444; /* Tailwind red-500 */
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

              // Green
              "hover:shadow-customGreen border-customGreen bg-darken-2 hover:border-customGreen hover:bg-transparent":
                !disabled && color === "green",

              // Orange
              "hover:shadow-orange-500 border-orange-500 bg-darken-2 hover:border-orange-500 hover:bg-transparent":
                !disabled && color === "orange",

              // Red
              "hover:shadow-red-500 border-red-500 bg-darken-2 hover:border-red-500 hover:bg-transparent":
                !disabled && color === "red",

              // Disabled
              "bg-darken border-gray-700 hover:bg-darken hover:border-gray-700 cursor-not-allowed":
                disabled,
            },
            className,
          )}
          disabled={isLoading || disabled}
        >
          {children}
          {text}
        </button>

        {isLoading && (
          <div
            className={clsx("animate-highlight", {
              "highlight-green": color === "green",
              "highlight-orange": color === "orange",
              "highlight-red": color === "red",
            })}
          />
        )}
      </div>
    </>
  );
}
