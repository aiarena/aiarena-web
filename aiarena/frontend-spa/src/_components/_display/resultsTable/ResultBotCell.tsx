import { Link } from "react-router";
import clsx from "clsx";

import { getIDFromBase64 } from "@/_lib/relayHelpers";
import { reverseUrl } from "@/_lib/reverseUrl";
import { formatWinnerName } from "@/_components/_display/formatWinnerName";

/** The parts of either participant a bot cell shows. */
type Participant =
  | {
      readonly eloChange?: number | null;
      readonly bot: { readonly id: string; readonly name: string };
    }
  | null
  | undefined;

export default function ResultBotCell({ participant, winnerName }: { participant: Participant; winnerName?: string | null }) {
  const name = participant?.bot.name || "";
  const label = formatWinnerName(winnerName ?? undefined, participant?.bot.name) || name;
  const botId = getIDFromBase64(participant?.bot.id, "BotType");
  const eloChange = participant?.eloChange;

  return (
    <span className="flex justify-between">
      {botId ? (
        <Link
          className="font-semibold text-gray-200 truncate mr-2"
          to={reverseUrl("bot", { pk: botId })}
          role="cell"
          aria-label={`View bot profile for ${name}, Bot`}
          title={name}
        >
          {label}
        </Link>
      ) : (
        <span className="font-semibold text-gray-200 truncate mr-2">{label}</span>
      )}
      <span className={clsx({ "text-red-400": eloChange && eloChange < 0 })}>{eloChange}</span>
    </span>
  );
}
