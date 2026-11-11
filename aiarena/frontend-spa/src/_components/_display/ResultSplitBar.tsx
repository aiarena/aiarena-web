import clsx from "clsx";

/**
 * Fill for non-crash losses. Losses are usually the biggest part of the bar
 * (a typical bot loses most games), so they're styled as a calm backdrop rather
 * than an alarm: deep burgundy with a fine, low-contrast stripe texture. That
 * keeps a mostly-loss bar pleasant to look at and leaves the eye on the wins.
 * Exported so legends can match.
 *
 * Every layer must be an image: Tailwind emits this as `background-image`, where
 * a bare color layer is invalid and silently drops the whole fill.
 */
export const LOSS_FILL =
  "bg-[repeating-linear-gradient(135deg,rgb(127_29_29/0.7)_0_2px,rgb(69_10_10)_2px_6px)]";

/** Fill for wins: the green with a soft top sheen, like a progress fill. */
export const WIN_FILL =
  "bg-[linear-gradient(180deg,rgb(170_225_95),rgb(134_194_50)_60%)]";

/** Fill for crashes: solid red — the part of losses that's the bot's own fault. */
export const CRASH_FILL = "bg-red-500";

type ResultSplitBarProps = {
  winPerc: number;
  tiePerc: number;
  lossPerc: number;
  /** Crashes are a subset of losses; shown as the solid end of the loss segment. */
  crashPerc: number;
  className?: string;
};

/** Horizontal win / tie / loss / crash split, as percentages (0–100). */
export default function ResultSplitBar({
  winPerc,
  tiePerc,
  lossPerc,
  crashPerc,
  className,
}: ResultSplitBarProps) {
  const segments = [
    { name: "wins", pct: winPerc, color: WIN_FILL },
    { name: "ties", pct: tiePerc, color: "bg-gray-500" },
    {
      name: "non-crash losses",
      pct: Math.max(lossPerc - crashPerc, 0),
      color: LOSS_FILL,
    },
    { name: "crashes", pct: crashPerc, color: CRASH_FILL },
  ];
  return (
    <div
      className={clsx(
        "flex h-2.5 w-full overflow-hidden rounded-full bg-neutral-700",
        className,
      )}
      role="img"
      aria-label={segments
        .map((s) => `${s.pct.toFixed(1)}% ${s.name}`)
        .join(", ")}
    >
      {segments.map((s) => (
        <div key={s.name} className={s.color} style={{ width: `${s.pct}%` }} />
      ))}
    </div>
  );
}
