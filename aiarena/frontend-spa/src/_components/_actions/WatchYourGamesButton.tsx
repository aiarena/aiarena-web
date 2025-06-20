import { getPublicPrefix } from "@/_lib/getPublicPrefix";
import { MouseEventHandler, ReactNode } from "react";
import { useNavigate } from "react-router";
import clsx from "clsx";

interface WatchYourGamesButtonProps {
  href?: string;
  children: ReactNode;
  onClick?: MouseEventHandler<HTMLButtonElement>;
  fullWidth?: boolean;
  className?: string;
}

export default function WatchYourGamesButton({
  onClick,
  href,
  children,
  fullWidth = false,
  className = "",
}: WatchYourGamesButtonProps) {
  const navigate = useNavigate();

  const handleRedirect = (path: string) => {
    try {
      if (/^https?:\/\//.test(path)) {
        window.open(path, "_blank");
      } else {
        navigate(path);
      }
    } catch (error) {
      console.error("Failed to navigate:", error);
    }
  };

  const handleClick: MouseEventHandler<HTMLButtonElement> = (event) => {
    if (onClick) {
      onClick(event);
    } else if (href) {
      handleRedirect(href);
    }
  };

  return (
    <button
      type="button"
      onClick={handleClick}
      className={clsx(
        "group relative overflow-hidden border-2 border-neutral-600 rounded transition-all duration-100 hover:border-customGreen hover:shadow-lg hover:shadow-customGreen/25",
        "bg-darken-2 px-6 py-2 flex items-center justify-center text-white font-semibold space-x-2",
        fullWidth ? "w-full" : "inline-block",

        className
      )}
    >
      {/* shimmer overlay */}
      <div className="absolute inset-0 -translate-x-full group-hover:translate-x-full transition-transform duration-700 bg-gradient-to-r from-transparent via-white/10 to-transparent skew-x-12" />

      <img
        src={`${getPublicPrefix()}/icons/twitch-icon.svg`}
        alt="Twitch Icon"
        height={18}
        width={18}
        className="inline-block align-middle invert mb-[2px] mr-2"
      />
      <span className="tracking-wide">{children}</span>
    </button>
  );
}
