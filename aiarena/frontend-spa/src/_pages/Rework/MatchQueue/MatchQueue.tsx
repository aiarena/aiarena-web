import { useState } from "react";
import { graphql, useLazyLoadQuery } from "react-relay";
import { Link } from "react-router";

import { getIDFromBase64 } from "@/_lib/relayHelpers";
import { reverseUrl } from "@/_lib/reverseUrl";
import Searchbar from "@/_components/_actions/Searchbar";
import NoItemsInListMessage from "@/_components/_display/NoItemsInListMessage";
import { MatchQueueQuery } from "./__generated__/MatchQueueQuery.graphql";
import MatchQueueTable from "./MatchQueueTable";

export default function MatchQueue() {
  const { matchQueue } = useLazyLoadQuery<MatchQueueQuery>(
    graphql`
      query MatchQueueQuery {
        matchQueue {
          requestedMatches {
            started
            ...MatchQueueTable_matches
          }
          rounds {
            round {
              id
              number
              competition {
                id
                name
              }
            }
            matches {
              started
              ...MatchQueueTable_matches
            }
          }
        }
      }
    `,
    {},
    // The queue changes constantly; never show a stale cached copy.
    { fetchPolicy: "store-and-network" },
  );
  const [filter, setFilter] = useState("");

  const allMatches = [
    ...matchQueue.requestedMatches,
    ...matchQueue.rounds.flatMap((r) => r.matches),
  ];
  const running = allMatches.filter((m) => m.started).length;

  if (allMatches.length === 0) {
    return (
      <NoItemsInListMessage>
        <p>The queue is empty. Queued matches will show here.</p>
      </NoItemsInListMessage>
    );
  }

  return (
    <section aria-labelledby="match-queue-heading">
      <div className="mb-6 flex flex-wrap items-end justify-between gap-4">
        <div>
          <h2 id="match-queue-heading" className="text-2xl font-semibold">
            Match Queue
          </h2>
          <p className="text-sm text-gray-300">
            {allMatches.length} matches waiting: {running} running,{" "}
            {allMatches.length - running} queued
          </p>
        </div>
        <Searchbar
          value={filter}
          onChange={setFilter}
          placeholder="Filter by bot, map, client or match ID..."
          aria-label="Filter the match queue"
          classNames="min-w-70"
        />
      </div>

      {matchQueue.requestedMatches.length > 0 && (
        <MatchQueueTable
          title="Requested matches"
          matches={matchQueue.requestedMatches}
          filter={filter}
        />
      )}

      {matchQueue.rounds.map(({ round, matches }) => (
        <MatchQueueTable
          key={round.id}
          matches={matches}
          filter={filter}
          title={
            <>
              <Link to={reverseUrl("round", { pk: getIDFromBase64(round.id, "RoundsType") })}>
                Round {round.number}
              </Link>{" "}
              <span className="text-gray-400">·</span>{" "}
              <Link
                to={reverseUrl("competition", {
                  pk: getIDFromBase64(round.competition.id, "CompetitionType"),
                })}
              >
                {round.competition.name}
              </Link>
            </>
          }
        />
      ))}
    </section>
  );
}
