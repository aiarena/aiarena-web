import React, { MouseEventHandler, useState } from "react";
import { useRouter } from "next/navigation";
import { off } from "process";

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
  const router = useRouter();
  const [isLoading, setIsLoading] = useState(false);

  const handleRedirect = async (path: string) => {
    setIsLoading(true);
    try {
      router.push(path);
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
    <>
      <style jsx>{`
        @keyframes highlight {
          0% {
            border-color: transparent;
            border-bottom-color: var(
              --customGreenHighlight1
            ); /* Start from the bottom */
          }
          25% {
            border-left-color: var(
              --customGreenHighlight1
            ); /* Move to the left */
          }
          50% {
            border-top-color: var(--customGreenHighlight1); /* Then the top */
          }
          75% {
            border-right-color: var(
              --customGreenHighlight1
            ); /* Finish at the right */
          }
          100% {
            border-color: transparent;
            border-bottom-color: var(
              --customGreenHighlight1
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
          border-radius: 9999px;
          animation: highlight 1s linear infinite;
          animation-delay: 0.15s;
        }
      `}</style>
      <div className="relative inline-block">
        <button
          onClick={handleClick}
          className={`${className} shadow shadow-black shadow-sm hover:shadow-lg hover:shadow-black relative z-10 hover:border-4 border-4 border-customGreen bg-customGreen hover:bg-transparent hover:border-customGreen text-white font-semibold py-3 px-8 rounded-full  transition duration-300 ease-in-out transform`}
          //   disabled={isLoading}
        >
          {text}
        </button>
        {isLoading && <div className="animate-highlight"></div>}
      </div>
    </>
  );
}
