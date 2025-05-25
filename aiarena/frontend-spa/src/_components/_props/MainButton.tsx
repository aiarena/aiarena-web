import React, { MouseEventHandler, useState } from "react";
import { useNavigate } from "react-router";

interface MainButtonProps {
  href?: string;
  text: string;
  className?: string;
  onClick?: MouseEventHandler<HTMLButtonElement>;
}

export default function MainButton({
  href,
  text,
  className,
  onClick,
}: MainButtonProps) {
  const [isLoading, setIsLoading] = useState(false);
  const navigate = useNavigate();
  const handleRedirect = async (path: string) => {
    setIsLoading(true);
    try {
      navigate(path);
    } catch (error) {
      console.error("Failed to navigate:", error);
    } finally {
      setIsLoading(false);
    }
  };

  const handleClick: React.MouseEventHandler<HTMLButtonElement> = (event) => {
    if (onClick) {
      onClick(event);
    } else if (href) {
      handleRedirect(href);
    }
  };

  return (
    <div className="relative inline-block">
      <style>{`
      @keyframes highlight-mainbutton {
        0% {
          border-color: transparent;
          border-bottom-color: var(--color-customGreen, #00ff88);
        }
        25% {
          border-left-color: var(--color-customGreen, #00ff88);
        }
        50% {
          border-top-color: var(--color-customGreen, #00ff88);
        }
        75% {
          border-right-color: var(--color-customGreen, #00ff88);
        }
        100% {
          border-color: transparent;
          border-bottom-color: var(--color-customGreen, #00ff88);
        }
      }

      .animate-highlight-mainbutton {
        position: absolute;
        top: -4px;
        left: -4px;
        width: calc(100% + 8px);
        height: calc(100% + 8px);
        border: 4px solid transparent;
        border-radius: 9999px;
        animation: highlight 1s linear infinite;
        pointer-events: none;
        z-index: 0;
        box-sizing: border-box;
      }
    `}</style>

      <button
        onClick={handleClick}
        className={`relative z-10 ${className ?? ""} shadow-sm shadow-black hover:shadow-customGreen border-3 border-customGreen bg-darken-2 hover:bg-transparent text-white font-semibold py-2 px-6 rounded-full transition duration-300 ease-in-out transform backdrop-blur-sm`}
      >
        {text}
      </button>

      {isLoading && <div className="animate-highlight-mainbutton"></div>}
    </div>
  );
}
