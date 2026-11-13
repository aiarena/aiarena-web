import { graphql, useFragment } from "react-relay";
import { Link } from "react-router";

import { getIDFromBase64 } from "@/_lib/relayHelpers";
import { reverseUrl } from "@/_lib/reverseUrl";
import timeAgoShort from "@/_lib/timeAgoSort";
import NoItemsInListMessage from "@/_components/_display/NoItemsInListMessage";
import { AssignedMatches_arenaClient$key } from "./__generated__/AssignedMatches_arenaClient.graphql";

interface AssignedMatchesProps {
  arenaClient: AssignedMatches_arenaClient$key;
}

function BotLink({ bot }: { bot: { readonly id: string; readonly name: string } | null | undefined }) {
  if (!bot) {
    return <span className="text-gray-400">?</span>;
  }
  return (
    <Link className="font-semibold text-gray-200" to={reverseUrl("bot", { pk: getIDFromBase64(bot.id, "BotType") })}>
      {bot.name}
    </Link>
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
          participant1 {
            id
            name
          }
          participant2 {
            id
            name
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
    <ul className="space-y-2">
      {assignedMatches.map((match) => (
        <li
          key={match.id}
          className="flex flex-wrap items-center justify-between gap-2 rounded-md border border-neutral-700 bg-darken-2 px-4 py-2 text-sm"
        >
          <span className="flex flex-wrap items-center gap-2">
            <Link
              className="text-gray-400 tabular-nums"
              to={reverseUrl("match", { pk: getIDFromBase64(match.id, "MatchType") })}
            >
              #{getIDFromBase64(match.id, "MatchType")}
            </Link>
            <BotLink bot={match.participant1} />
            <span className="text-gray-500">vs</span>
            <BotLink bot={match.participant2} />
            <span className="text-gray-500">on</span>
            <span className="text-gray-300">{match.map.name}</span>
          </span>
          <span className="text-gray-400">
            {match.started ? `Started ${timeAgoShort(match.started)} ago` : "Queued"}
          </span>
        </li>
      ))}
    </ul>
  );
}
