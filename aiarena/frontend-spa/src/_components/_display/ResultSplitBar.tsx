import clsx from "clsx";

type ResultSplitBarProps = {
  winPerc: number;
  tiePerc: number;
  lossPerc: number;
  className?: string;
};

/** Horizontal win / tie / loss split, as percentages (0–100). */
export default function ResultSplitBar({
  winPerc,
  tiePerc,
  lossPerc,
  className,
}: ResultSplitBarProps) {
  const segments = [
    { name: "wins", pct: winPerc, color: "bg-customGreen" },
    { name: "ties", pct: tiePerc, color: "bg-gray-500" },
    { name: "losses", pct: lossPerc, color: "bg-red-500" },
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
