import { graphql, useFragment } from "react-relay";
import type { Summary_node$key } from "./__generated__/Summary_node.graphql";

type SummaryProps = {
  data: Summary_node$key;
};

function fmtPct(v: number | null | undefined) {
  return typeof v === "number" ? `${v.toFixed(1)}%` : "—";
}

function fmtNum(v: number | null | undefined, digits = 0) {
  return typeof v === "number" ? v.toFixed(digits) : "—";
}

export default function Summary(props: SummaryProps) {
  const data = useFragment(
    graphql`
      fragment Summary_node on CompetitionParticipationType {
        competition {
          id
          name
        }
        bot {
          id
          name
        }
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
    props.data
  );

  return (
    <div className="  p-4 rounded-xl border border-neutral-800 bg-darken-2 backdrop-blur-lg shadow-lg">
      <div className="grid grid-cols-2 md:grid-cols-4 gap-3 mt-4 mb-4">
        <Stat label="Current Elo" value={fmtNum(data.elo)} />
        <Stat label="Highest Elo" value={fmtNum(data.highestElo)} />
        <Stat label="Matches" value={String(data.matchCount ?? "—")} />
        <Stat label="Crashes" value={String(data.crashCount ?? "—")} />
      </div>
      <div className="grid grid-cols-2 md:grid-cols-3 gap-3 ">
        <Stat label="Wins" value={String(data.winCount ?? "—")} />
        <Stat label="Losses" value={String(data.lossCount ?? "—")} />
        <Stat label="Ties" value={String(data.tieCount ?? "—")} />
        <Stat label="Win %" value={fmtPct(data.winPerc)} />
        <Stat label="Loss %" value={fmtPct(data.lossPerc)} />
        <Stat label="Tie %" value={fmtPct(data.tiePerc)} />
      </div>
    </div>
  );
}

function Stat({ label, value }: { label: string; value: string }) {
  return (
    <div className="rounded-lg border border-neutral-800 bg-black/20 px-3 py-2">
      <div className=" text-gray-400">{label}</div>
      <div className="font-semibold text-gray-100">{value}</div>
    </div>
  );
}
