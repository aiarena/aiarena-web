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
        status
        map {
          downloadLink
          name
        }
        participant1 {
          id
          name
          id
          type
          playsRace {
            name
          }
        }
        participant2 {
          id
          name
          id
          type
          playsRace {
            name
          }
        }
        result {
          gameTimeFormatted
          replayFile
          arenaclientLog
          winner {
            name
            id
          }
          participant1 {
            eloChange
            id
            matchLog
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
            matchLog
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
  const mp1 = match.participant1;
  const p2 = match.result?.participant2;
  const mp2 = match.participant2;
  const winner = match.result?.winner;

  const matchFinished = match.status === "Finished";

  const getEloClass = (eloChange?: number | null) =>
    clsx(
      eloChange && eloChange > 0
        ? "text-customGreen"
        : eloChange && eloChange < 0
          ? "text-red-500"
          : "text-gray-300"
    );

  return (
    <div className="mb-8 rounded-2xl border border-neutral-800 bg-darken-2 p-4 sm:p-5 shadow-lg shadow-black">
      <div className="block sm:flex justify-between w-full  mb-6">
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
            <span className="text-xl font-semibold text-white ml-auto">
              {matchFinished ? (
                <>
                  {winner ? (
                    <span className="flex flex-wrap justify-end">
                      <a
                        href={`/bots/${getIDFromBase64(winner.id, "BotType")}`}
                        className="block truncate max-w-80 mr-2 overflow-ellipsis"
                      >
                        {winner.name}
                      </a>
                      won the match
                    </span>
                  ) : (
                    "Match completed"
                  )}
                </>
              ) : (
                match.status
              )}
            </span>

            {match.result?.replayFile && (
              <div className="w-full flex justify-end">
                <a
                  download
                  href={`${match.result.replayFile}`}
                  className="text-customGreen hover:underline whitespace-nowrap text-lg flex items-center gap-1"
                >
                  <ArrowDownCircleIcon height={18} /> Replay
                </a>
              </div>
            )}
            {match.result?.arenaclientLog && (
              <div className="w-full flex justify-end">
                <a
                  download
                  href={`${match.result.arenaclientLog}`}
                  className="text-customGreen hover:underline whitespace-nowrap text-lg flex items-center gap-1"
                >
                  <ArrowDownCircleIcon height={18} /> Arenaclient Logs
                </a>
              </div>
            )}

            {match.result?.participant1?.matchLog && (
              <div className="w-full flex justify-end">
                <a
                  download
                  href={`/${match.result?.participant1?.matchLog}`}
                  className="text-customGreen hover:underline whitespace-nowrap text-lg flex items-center gap-1"
                >
                  <ArrowDownCircleIcon height={18} />{" "}
                  {match.result?.participant1.bot.name} Logs
                </a>
              </div>
            )}
            {match.result?.participant2?.matchLog && (
              <div className="w-full flex justify-end">
                <a
                  download
                  href={`/${match.result?.participant2?.matchLog}`}
                  className="text-customGreen hover:underline whitespace-nowrap text-lg flex items-center gap-1"
                >
                  <ArrowDownCircleIcon height={18} />{" "}
                  {match.result?.participant2.bot.name} Logs
                </a>
              </div>
            )}
          </div>
        </div>
      </div>
      <div className="mt-2 rounded-lg border border-neutral-700 bg-neutral-900/90 p-3 sm:p-4">
        <div className="block sm:flex  items-center gap-2 text-gray-200 flex-row justify-between">
          {/* Participant 1 */}
          {mp1 && (
            <div className="font-medium flex flex-col items-center md:items-start gap-1 min-w-0">
              <>
                <a
                  href={`/bots/${getIDFromBase64(mp1.id, "BotType")}`}
                  className="text-white hover:text-customGreen truncate max-w-[180px] sm:max-w-xs text-xl"
                >
                  {formatWinnerName(winner?.name, mp1.name)}
                </a>
                {p1 && (
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
                )}

                <span className="text-gray-400">{mp1.playsRace.name}</span>
                <RenderCodeLanguage type={`${mp1.type}`} muted />
              </>
            </div>
          )}

          {/* VS Divider */}
          <div className="flex flex-col items-center mx-2 my-16 sm:my-1  text-gray-400">
            {matchFinished ? (
              <div className="inline-flex items-center justify-center rounded-full bg-neutral-900/80 border border-customGreen p-1.5 shadow-black mb-2">
                <TrophyIcon
                  className="h-7 w-7 text-customGreen"
                  aria-hidden="true"
                />
              </div>
            ) : (
              match.status
            )}
            <span className="hidden md:inline ">VS</span>
            <span className="md:hidden">- VS -</span>
          </div>

          {/* Participant 2 */}
          <div className="flex flex-col items-center md:items-end gap-1 min-w-0">
            {mp2 && (
              <>
                <a
                  href={`/bots/${getIDFromBase64(mp2.id, "BotType")}`}
                  className="font-medium text-white hover:text-customGreen truncate max-w-[180px] sm:max-w-xs text-xl"
                >
                  {formatWinnerName(winner?.name, mp2.name)}
                </a>
                {p2 && (
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
                )}
                <span className="text-gray-400">{mp2.playsRace.name}</span>
                <RenderCodeLanguage type={`${mp2.type}`} muted />
              </>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
