import { CoreMatchParticipationResultChoices } from "@/_pages/Rework/Bot/__generated__/BotResultsTable_bot.graphql";

export function RenderResult({
  result,
}: {
  result: CoreMatchParticipationResultChoices | null | undefined | "";
}) {
  if (result === null || result === undefined || result === "") {
    return "";
  }

  const key = result.toLowerCase();

  if (key === "win") {
    return <span style={{ color: "rgb(0,255,0)" }}>Win</span>;
  }
  if (key === "loss") {
    return <span className="text-red-400">Loss</span>;
  }
  if (key === "tie") {
    return <span className="text-amber-300">Tie</span>;
  }

  return key ?? result;
}
