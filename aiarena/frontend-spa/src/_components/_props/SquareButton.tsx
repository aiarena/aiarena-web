import React, { MouseEventHandler } from "react";
import { useNavigate } from "react-router";

interface SquareButtonProps {
  href?: string;
  text?: string;
  className?: string;
  outerClassName?: string;
  onClick?: MouseEventHandler<HTMLButtonElement>;
  isLoading?: boolean;
  disabled?: boolean;
  children?: React.ReactNode;
}

export default function SquareButton({
  href,
  text,
  className,
  outerClassName,
  onClick,
  isLoading,
  disabled,
  children,
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
            border-bottom-color: var(
               --color-customGreen
            ); /* Start from the bottom */
          }
          25% {
            border-left-color: var(
              --color-customGreen
            ); /* Move to the left */
          }
          50% {
            border-top-color: var( --color-customGreen); /* Then the top */
          }
          75% {
            border-right-color: var(
              --color-customGreen
            ); /* Finish at the right */
          }
          100% {
            border-color: transparent;
            border-bottom-color: var(
              --color-customGreen
            ); /* Loop back to the bottom */
          }
        }
        .animate-highlight {
          position: absolute;
          top: -4px;
          left: -4px;
          width: calc(100% + 8px);
          height: calc(100% + 8px);
          border: 4px solid transparent;
          border-radius: 7px;
          animation: highlight 1s linear infinite;
          animation-delay: 0.15s;
        }
      `}</style>
      <div className={`relative inline-block ${outerClassName}`}>
        <button
          onClick={handleClick}
          className={` flex justify-center items-center w-full shadow-sm shadow-black border-1 text-white font-semibold py-1 px-2 rounded-sm transition duration-300 ease-in-out transform
            ${
              !disabled
                ? "hover:shadow-customGreen border-customGreen bg-darken-2 hover:border-customGreen hover:bg-transparent"
                : "bg-darken border-gray-700 hover:bg-darken hover:border-gray-700 "
            }
            ${className}`}
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
