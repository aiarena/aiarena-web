import clsx from "clsx";

interface MatchQueueStatsProps {
  running: number;
  queued: number;
}

function Stat({
  label,
  value,
  live,
}: {
  label: string;
  value: number;
  /** Green count with a pulsing dot: things happening right now. */
  live?: boolean;
}) {
  return (
    <div
      role="group"
      aria-label={label}
      className="flex items-baseline gap-2 rounded-lg border border-neutral-700 bg-neutral-900/90 px-3 py-1.5"
    >
      {live && (
        <span
          className="h-2 w-2 self-center animate-pulse rounded-full bg-customGreen"
          aria-hidden="true"
        />
      )}
      <dd
        className={clsx(
          "text-lg font-semibold tabular-nums",
          live ? "text-customGreen" : "text-white",
        )}
      >
        {value.toLocaleString()}
      </dd>
      <dt className="text-sm text-gray-400">{label}</dt>
    </div>
  );
}

/** Headline numbers for the queue: matches running vs. still queued. */
export default function MatchQueueStats({
  running,
  queued,
}: MatchQueueStatsProps) {
  return (
    <dl className="flex flex-wrap gap-2">
      <Stat label="Running" value={running} live />
      <Stat label="Queued" value={queued} />
    </dl>
  );
}
