import { ReactNode } from "react";
import { graphql, useFragment } from "react-relay";
import { Link } from "react-router";
import clsx from "clsx";

import { getIDFromBase64 } from "@/_lib/relayHelpers";
import { reverseUrl } from "@/_lib/reverseUrl";
import TimeAgo from "@/_components/_display/TimeAgo";
import NoItemsInListMessage from "@/_components/_display/NoItemsInListMessage";
import { RenderRace } from "@/_components/_display/RenderRace";
import RenderCodeLanguage from "@/_components/_display/RenderCodeLanguage";
import {
  AssignedMatches_arenaClient$data,
  AssignedMatches_arenaClient$key,
} from "./__generated__/AssignedMatches_arenaClient.graphql";

interface AssignedMatchesProps {
  arenaClient: AssignedMatches_arenaClient$key;
}

type AssignedMatch = AssignedMatches_arenaClient$data["assignedMatches"][number];
type Bot = AssignedMatch["participant1"];

/** A "Label value" row under the bot name, e.g. "Race [icon] Zerg". */
function BotDetail({ label, children }: { label: string; children: ReactNode }) {
  return (
    <div className="flex min-w-0 max-w-full items-center gap-2 text-sm text-gray-300">
      <span className="shrink-0 text-gray-400">{label}</span>
      {children}
    </div>
  );
}

function BotSide({ bot, align }: { bot: Bot; align: "left" | "right" }) {
  if (!bot) {
    return <div className="flex-1 text-gray-400">Unknown bot</div>;
  }
  return (
    <div
      className={clsx(
        "flex min-w-0 flex-1 flex-col gap-1",
        align === "right" && "items-end text-right",
      )}
    >
      <div className="flex min-w-0 max-w-full items-baseline gap-2">
        <span className="shrink-0 text-sm text-gray-400">Bot</span>
        <Link
          className="truncate text-lg font-semibold text-gray-100"
          to={reverseUrl("bot", { pk: getIDFromBase64(bot.id, "BotType") })}
          title={bot.name}
        >
          {bot.name}
        </Link>
      </div>
      <BotDetail label="Race">
        <RenderRace race={bot.playsRace} />
      </BotDetail>
      <BotDetail label="Language">
        <RenderCodeLanguage type={bot.type ?? ""} muted />
      </BotDetail>
      {/* Who wrote it, set apart from the bot's own properties above */}
      <div
        className={clsx(
          "mt-2 flex w-full flex-col border-t border-neutral-700 pt-2",
          align === "right" && "items-end",
        )}
      >
        <BotDetail label="Author">
          <Link
            className="truncate text-gray-300"
            to={reverseUrl("author", { pk: getIDFromBase64(bot.user.id, "UserType") })}
          >
            {bot.user.username}
          </Link>
        </BotDetail>
      </div>
    </div>
  );
}

function AssignedMatchCard({ match }: { match: AssignedMatch }) {
  const matchId = getIDFromBase64(match.id, "MatchType");

  return (
    <article className="rounded-2xl border border-neutral-800 bg-darken-2 p-4 sm:p-5 shadow-lg shadow-black backdrop-blur-sm">
      <header className="mb-4 flex flex-wrap items-center justify-between gap-2">
        <div className="flex min-w-0 flex-col gap-1">
          <span className="text-lg font-semibold">
            <span className="text-gray-400">Match ID </span>
            <Link className="text-white" to={reverseUrl("match", { pk: matchId })}>
              {matchId}
            </Link>
          </span>
          {match.round ? (
            <span className="text-sm text-gray-300">
              <span className="text-gray-400">Competition </span>
              <Link
                to={reverseUrl("competition", {
                  pk: getIDFromBase64(match.round.competition.id, "CompetitionType"),
                })}
              >
                {match.round.competition.name}
              </Link>
              <span className="text-gray-400"> · </span>
              <Link to={reverseUrl("round", { pk: getIDFromBase64(match.round.id, "RoundsType") })}>
                Round {match.round.number}
              </Link>
            </span>
          ) : match.requestedBy ? (
            <span className="text-sm text-gray-300">
              <span className="text-gray-400">Requested by </span>
              <Link
                to={reverseUrl("author", {
                  pk: getIDFromBase64(match.requestedBy.id, "UserType"),
                })}
              >
                {match.requestedBy.username}
              </Link>
            </span>
          ) : null}
        </div>
        {match.started ? (
          <span className="flex items-center gap-2 rounded-full border border-customGreen/60 bg-customGreen/10 px-3 py-0.5 text-sm text-customGreen">
            <span className="h-2 w-2 rounded-full bg-customGreen" aria-hidden="true" />
            In progress · <TimeAgo since={match.started} />
          </span>
        ) : (
          <span className="rounded-full border border-neutral-600 bg-neutral-800 px-3 py-0.5 text-sm text-gray-400">
            Queued
          </span>
        )}
      </header>

      <div className="flex items-center gap-4">
        <BotSide bot={match.participant1} align="left" />
        <span className="shrink-0 text-sm font-semibold uppercase text-gray-400">vs</span>
        <BotSide bot={match.participant2} align="right" />
      </div>

      <footer className="mt-4 border-t border-neutral-700 pt-3 text-sm text-gray-300">
        <span className="text-gray-400">Map </span>
        {match.map.name}
      </footer>
    </article>
  );
}

export default function AssignedMatches(props: AssignedMatchesProps) {
  const { assignedMatches } = useFragment(
    graphql`
      fragment AssignedMatches_arenaClient on ArenaClientType {
        assignedMatches {
          id
          started
          map {
            name
          }
          round {
            id
            number
            competition {
              id
              name
            }
          }
          requestedBy {
            id
            username
          }
          participant1 {
            id
            name
            type
            playsRace {
              name
              label
            }
            user {
              id
              username
            }
          }
          participant2 {
            id
            name
            type
            playsRace {
              name
              label
            }
            user {
              id
              username
            }
          }
        }
      }
    `,
    props.arenaClient,
  );

  if (assignedMatches.length === 0) {
    return (
      <NoItemsInListMessage>
        <p>No matches assigned right now.</p>
      </NoItemsInListMessage>
    );
  }

  return (
    <div className="grid gap-4">
      {assignedMatches.map((match) => (
        <AssignedMatchCard key={match.id} match={match} />
      ))}
    </div>
  );
}
