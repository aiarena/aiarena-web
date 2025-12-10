import { graphql, useFragment } from "react-relay";
import { MatchDecal_match$key } from "./__generated__/MatchDecal_match.graphql";
import EloTrendIcon from "@/_components/_display/EloTrendIcon";
import { getIDFromBase64 } from "@/_lib/relayHelpers";
import { formatWinnerName } from "@/_components/_display/formatWinnerName";
import { ArrowDownCircleIcon, TrophyIcon } from "@heroicons/react/24/outline";
import clsx from "clsx";
import RenderCodeLanguage from "@/_components/_display/RenderCodeLanguage";
interface MatchDecalProps {
  match: MatchDecal_match$key;
}

export default function MatchInfo(props: MatchDecalProps) {
  const match = useFragment(
    graphql`
      fragment MatchDecal_match on MatchType {
        id
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
              type
              playsRace {
                name
              }
            }
          }
          participant2 {
            eloChange
            id
            bot {
              id
              name
              type
              playsRace {
                name
              }
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
      <div className="flex justify-between w-full  mb-6">
        <h2 id="match-heading" className="sr-only">
          Match {match.id}
        </h2>

        <div className="items-baseline gap-2">
          <div className="flex">
            <h2
              id="bot-information-heading"
              className="text-xl sm:text-2xl font-semibold text-white"
            >
              Match {getIDFromBase64(match.id, "MatchType")}
            </h2>
          </div>
          <span className="ml-2 flex gap-2 text-lg">
            on{" "}
            <a
              href={`${match.map.downloadLink}`}
              className="flex gap-1 items-center"
            >
              <ArrowDownCircleIcon height={18} /> {match.map.name}
            </a>
          </span>
        </div>

        <div className="flex items-center justify-between mb-3 flex-wrap">
          <div className="mb-3 flex flex-col gap-1 w-full">
            <span className="text-xl font-semibold text-white">
              {winnerName ? (
                <span className="flex">
                  <span className="block truncate max-w-80 mr-2 overflow-ellipsis">
                    {winnerName}
                  </span>{" "}
                  won the match
                </span>
              ) : (
                "Match completed"
              )}
            </span>

            {match.result?.replayFile ? (
              <div className="w-full flex justify-end">
                <a
                  href={match.result.replayFile}
                  className="text-customGreen hover:underline whitespace-nowrap"
                >
                  Download replay
                </a>
              </div>
            ) : null}
          </div>
        </div>
      </div>
      <div className="mt-2 rounded-lg border border-neutral-700 bg-neutral-900/90 p-3 sm:p-4">
        <div className="flex items-center gap-2 text-gray-200 flex-row justify-between">
          {/* Participant 1 */}
          <div className="font-medium flex flex-col items-center md:items-start gap-1 min-w-0">
            <a
              href={`/bots/${getIDFromBase64(p1.bot.id, "BotType")}`}
              className="text-white hover:text-customGreen truncate max-w-[180px] sm:max-w-xs text-xl"
            >
              {formatWinnerName(winnerName, p1.bot.name)}
            </a>

            <div className="flex items-center gap-1 mb-4 text-lg">
              <span className={getEloClass(p1.eloChange)}>
                {p1.eloChange
                  ? p1.eloChange > 0
                    ? `+${p1.eloChange}`
                    : p1.eloChange
                  : "0"}
              </span>
              <EloTrendIcon trend={p1.eloChange} />
            </div>
            <span className="text-gray-400">{p1.bot.playsRace.name}</span>
            <RenderCodeLanguage type={`${p1.bot.type}`} muted />
          </div>

          {/* VS Divider */}
          <div className="flex flex-col items-center mx-2 my-1  text-gray-400">
            <div className="inline-flex items-center justify-center rounded-full bg-neutral-900/80 border border-customGreen p-1.5 shadow-black mb-2">
              <TrophyIcon
                className="h-7 w-7 text-customGreen"
                aria-hidden="true"
              />
            </div>
            <span className="hidden md:inline ">VS</span>
            <span className="md:hidden">- VS -</span>
          </div>

          {/* Participant 2 */}
          <div className="flex flex-col items-center md:items-end gap-1 min-w-0">
            <a
              href={`/bots/${getIDFromBase64(p2.bot.id, "BotType")}`}
              className="font-medium text-white hover:text-customGreen truncate max-w-[180px] sm:max-w-xs text-xl"
            >
              {formatWinnerName(winnerName, p2.bot.name)}
            </a>

            <div className="flex items-center gap-1 mb-4 text-lg">
              <span className={getEloClass(p2.eloChange)}>
                {p2.eloChange
                  ? p2.eloChange > 0
                    ? `+${p2.eloChange}`
                    : p2.eloChange
                  : "0"}
              </span>
              <EloTrendIcon trend={p2.eloChange} />
            </div>
            <span className="text-gray-400">{p2.bot.playsRace.name}</span>
            <RenderCodeLanguage type={`${p2.bot.type}`} muted />
          </div>
        </div>
      </div>
    </div>
  );
}
