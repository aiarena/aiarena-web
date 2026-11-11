import { MouseEventHandler, ReactNode } from "react";
import { Link } from "react-router";
import clsx from "clsx";

type AiGlowButtonProps = {
  children: ReactNode;
  className?: string;
  title?: string;
  "aria-label"?: string;
} & (
  | { to: string; onClick?: never }
  | { to?: never; onClick: MouseEventHandler<HTMLButtonElement> }
);

/**
 * Compact pill with a thin animated green border — a light sweeps around it
 * while it softly pulses. Renders a router `Link` when given `to`, otherwise
 * a `button`.
 */
export default function AiGlowButton({
  children,
  className,
  title,
  "aria-label": ariaLabel,
  ...action
}: AiGlowButtonProps) {
  const classes = clsx(
    "ai-glow inline-flex items-center rounded-full px-2.5 py-0.5 text-sm font-medium",
    className,
  );
  const content = <span className="ai-glow-text">{children}</span>;

  if (action.to !== undefined) {
    return (
      <Link
        to={action.to}
        className={classes}
        title={title}
        aria-label={ariaLabel}
      >
        {content}
      </Link>
    );
  }
  return (
    <button
      type="button"
      onClick={action.onClick}
      className={classes}
      title={title}
      aria-label={ariaLabel}
    >
      {content}
    </button>
  );
}
