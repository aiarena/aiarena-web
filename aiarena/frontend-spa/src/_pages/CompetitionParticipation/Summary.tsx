import clsx from "clsx";
import { graphql, useFragment } from "react-relay";
import { ExclamationTriangleIcon } from "@heroicons/react/24/outline";
import ResultSplitBar, {
  CRASH_FILL,
  LOSS_FILL,
  WIN_FILL,
} from "@/_components/_display/ResultSplitBar";
import type { Summary_node$key } from "./__generated__/Summary_node.graphql";

type SummaryProps = {
  data: Summary_node$key;
};

function fmtPct(v: number | null | undefined) {
  return typeof v === "number" ? `${v.toFixed(1)}%` : "—";
}

function fmtNum(v: number | null | undefined) {
  return typeof v === "number" ? v.toFixed(0) : "—";
}

export default function Summary(props: SummaryProps) {
  const data = useFragment(
    graphql`
      fragment Summary_node on CompetitionParticipationType {
        highestElo
        elo
        matchCount
        winCount
        tieCount
        lossCount
        crashCount
        winPerc
        lossPerc
        tiePerc
      }
    `,
    props.data,
  );

  const crashes = data.crashCount ?? 0;
  const crashPerc =
    data.matchCount > 0 ? (crashes / data.matchCount) * 100 : null;
  const atPeak =
    typeof data.highestElo === "number" && data.elo >= data.highestElo;

  const results = [
    {
      name: "Wins",
      count: data.winCount,
      pct: data.winPerc,
      rateLabel: "Win rate",
      color: WIN_FILL,
      valueColor: "text-customGreen",
    },
    {
      name: "Ties",
      count: data.tieCount,
      pct: data.tiePerc,
      rateLabel: "Tie rate",
      color: "bg-gray-500",
      valueColor: "text-gray-300",
    },
    {
      name: "Losses",
      count: data.lossCount,
      pct: data.lossPerc,
      rateLabel: "Loss rate",
      color: LOSS_FILL,
      valueColor: "text-red-500",
    },
  ];

  return (
    <section
      aria-labelledby="participation-summary-heading"
      className="rounded-2xl border border-neutral-800 bg-darken-2 p-4 sm:p-5 shadow-lg shadow-black backdrop-blur-sm"
    >
      <h3 id="participation-summary-heading" className="sr-only">
        Summary
      </h3>

      <div className="rounded-lg border border-neutral-700 bg-neutral-900/90 p-4 sm:p-6">
        <div className="grid gap-8 md:grid-cols-3 items-center">
          {/* Elo */}
          <div className="flex flex-col items-center md:items-start gap-1">
            <span className="text-sm font-semibold tracking-wide text-gray-400 uppercase">
              Current Elo
            </span>
            <span className="text-5xl tabular-nums text-white">
              {fmtNum(data.elo)}
            </span>
            <span className="text-sm text-gray-400">
              {atPeak ? (
                <span className="text-gray-100">At peak</span>
              ) : (
                <>
                  Peak{" "}
                  <span className="text-gray-100 tabular-nums">
                    {fmtNum(data.highestElo)}
                  </span>
                </>
              )}
            </span>
          </div>

          {/* Win rate */}
          <div className="flex flex-col items-center gap-2 w-full">
            <div className="grid w-full grid-cols-3 items-end gap-2">
              {results.map((r, i) => (
                <div
                  key={r.name}
                  className={clsx(
                    "flex flex-col",
                    i === 0
                      ? "items-start"
                      : i === 1
                        ? "items-center"
                        : "items-end",
                  )}
                >
                  <span className="text-xs font-semibold tracking-wide text-gray-400 uppercase">
                    {r.rateLabel}
                  </span>
                  <span className={clsx("text-2xl tabular-nums", r.valueColor)}>
                    {fmtPct(r.pct)}
                  </span>
                </div>
              ))}
            </div>
            <ResultSplitBar
              winPerc={data.winPerc}
              tiePerc={data.tiePerc}
              lossPerc={data.lossPerc}
              crashPerc={crashPerc ?? 0}
            />
            <div className="flex flex-wrap justify-center gap-x-4 gap-y-1 text-sm tabular-nums text-gray-400">
              {results.map((r) => (
                <span key={r.name} className="flex items-center gap-1.5">
                  <span
                    className={clsx(
                      "inline-block size-2.5 rounded-sm",
                      r.color,
                    )}
                  />
                  {r.name} <span className="text-gray-100">{r.count}</span>
                </span>
              ))}
              {crashes > 0 && (
                <span className="flex items-center gap-1.5">
                  <span
                    className={clsx("inline-block size-2.5 rounded-sm", CRASH_FILL)}
                  />
                  of which crashes{" "}
                  <span className="text-gray-100">{crashes}</span>
                </span>
              )}
            </div>
            <span className="text-sm text-gray-400">
              {data.matchCount} matches
            </span>
          </div>

          {/* Crashes */}
          <div className="flex flex-col items-center md:items-end gap-1">
            <span className="text-sm font-semibold tracking-wide text-gray-400 uppercase">
              Crashes
            </span>
            <span
              className={clsx(
                "flex items-center gap-2 text-5xl  tabular-nums",
                crashes > 0 ? "text-red-500" : "text-white",
              )}
            >
              {crashes > 0 && (
                <ExclamationTriangleIcon
                  className="size-[1em] shrink-0 pt-1"
                  aria-hidden
                />
              )}
              {crashes}
            </span>
            <span className="text-sm text-gray-400">
              {crashPerc === null ? (
                "No matches yet"
              ) : (
                <>
                  <span className="text-gray-100">{fmtPct(crashPerc)}</span> of
                  matches
                </>
              )}
            </span>
          </div>
        </div>
      </div>
    </section>
  );
}
