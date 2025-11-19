import { graphql, useFragment } from "react-relay";
import { MatchDecal_match$key } from "./__generated__/MatchDecal_match.graphql";
import EloTrendIcon from "@/_components/_display/EloTrendIcon";
import { getIDFromBase64 } from "@/_lib/relayHelpers";
import { formatWinnerName } from "@/_components/_display/formatWinnerName";
import { TrophyIcon } from "@heroicons/react/24/outline";
import clsx from "clsx";
interface MatchDecalProps {
  match: MatchDecal_match$key;
}

export default function MatchInfo(props: MatchDecalProps) {
  const match = useFragment(
    graphql`
      fragment MatchDecal_match on MatchType {
        map {
          downloadLink
          name
        }
        result {
          gameTimeFormatted
          replayFile
          winner {
            name
            id
          }
          participant1 {
            eloChange
            id
            bot {
              name
              id
            }
          }
          participant2 {
            eloChange
            id
            bot {
              id
              name
            }
          }
        }
      }
    `,
    props.match
  );

  const p1 = match.result?.participant1;
  const p2 = match.result?.participant2;
  const winnerName = match.result?.winner?.name;

  const getEloClass = (eloChange?: number | null) =>
    clsx(
      "text-xs sm:text-sm font-medium",
      eloChange && eloChange > 0
        ? "text-customGreen"
        : eloChange && eloChange < 0
          ? "text-red-500"
          : "text-gray-300"
    );

  if (!p1 || !p2) {
    return null;
  }

  return (
    <div className="mb-8 rounded-2xl border border-neutral-800 bg-darken-2 p-4 sm:p-5 shadow-lg shadow-black">
      <div className="flex items-center justify-between gap-3 mb-3 flex-wrap">
        <div className="flex items-center gap-2">
          <div className="inline-flex items-center justify-center rounded-full bg-neutral-900/80 border border-customGreen p-1.5 shadow-black mr-2">
            <TrophyIcon
              className="h-5 w-5 text-customGreen"
              aria-hidden="true"
            />
          </div>
          <div className="flex flex-col">
            <span className="text-xs uppercase tracking-wide text-gray-400">
              Match Result
            </span>
            <span className="text-xl font-semibold text-white">
              {winnerName ? `${winnerName} won the match` : "Match completed"}
            </span>

            <div className="flex gap-2 ml-2">
              {match.result?.replayFile ? (
                <a
                  href={match.result.replayFile}
                  className="text-customGreen hover:underline"
                >
                  Download replay
                </a>
              ) : null}
            </div>
          </div>
        </div>
      </div>

      <div className="mt-2 rounded-lg border border-neutral-700 bg-neutral-900/90 p-3 sm:p-4">
        <div className="flex flex-col items-center gap-2 text-sm sm:text-base text-gray-200 md:flex-row md:justify-between">
          {/* Participant 1 */}
          <div className="flex flex-col items-center md:items-start gap-1 min-w-0">
            <a
              href={`/bots/${getIDFromBase64(p1.bot.id, "BotType")}`}
              className="font-semibold text-white hover:text-customGreen truncate max-w-[180px] sm:max-w-xs"
            >
              {formatWinnerName(winnerName, p1.bot.name)}
            </a>
            <div className="flex items-center gap-1">
              <EloTrendIcon trend={p1.eloChange} />
              <span className={getEloClass(p1.eloChange)}>
                {p1.eloChange
                  ? p1.eloChange > 0
                    ? `+${p1.eloChange}`
                    : p1.eloChange
                  : "0"}
              </span>
            </div>
          </div>

          {/* VS Divider */}
          <div className="flex flex-col items-center mx-2 my-1 text-xs uppercase tracking-wide text-gray-400">
            <span className="hidden md:inline">VS</span>
            <span className="md:hidden">- VS -</span>
          </div>

          {/* Participant 2 */}
          <div className="flex flex-col items-center md:items-end gap-1 min-w-0">
            <a
              href={`/bots/${getIDFromBase64(p2.bot.id, "BotType")}`}
              className="font-semibold text-white hover:text-customGreen truncate max-w-[180px] sm:max-w-xs"
            >
              {formatWinnerName(winnerName, p2.bot.name)}
            </a>
            <div className="flex items-center gap-1">
              <span className={getEloClass(p2.eloChange)}>
                {p2.eloChange
                  ? p2.eloChange > 0
                    ? `+${p2.eloChange}`
                    : p2.eloChange
                  : "0"}
              </span>
              <EloTrendIcon trend={p2.eloChange} />
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
