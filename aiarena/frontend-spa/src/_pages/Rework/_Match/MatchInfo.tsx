import { graphql, useFragment } from "react-relay";
import { MatchInfo_match$key } from "./__generated__/MatchInfo_match.graphql";
import { getIDFromBase64 } from "@/_lib/relayHelpers";
import { getDateTimeISOString } from "@/_lib/dateUtils";

interface MatchInfoProps {
  match: MatchInfo_match$key;
}

export default function MatchInfo(props: MatchInfoProps) {
  const match = useFragment(
    graphql`
      fragment MatchInfo_match on MatchType {
        assignedTo {
          id
          username
        }
        result {
          gameTimeFormatted
          winner {
            name
            id
          }
          replayFile
          type
          started
        }
        round {
          id
          number
          competition {
            id
            name
          }
        }
        map {
          name
          downloadLink
        }
        started
        status
        created
        requestedBy {
          username
          id
        }
      }
    `,
    props.match
  );

  return (
    <div className="mb-8 rounded-2xl border border-neutral-800 bg-darken-2 p-5 sm:p-6 shadow-lg shadow-black space-y-6">
      <div>
        <h3 className="text-lg sm:text-xl font-semibold text-white mb-1">
          Match Information
        </h3>
      </div>

      <div className="rounded-lg border border-neutral-700 bg-neutral-900/60 p-4 space-y-2 text-sm sm:text-base text-gray-200">
        <div className="flex gap-2">
          <dt className="w-32 text-gray-400">Started</dt>
          <dd>{getDateTimeISOString(match.started) || "--"}</dd>
        </div>

        <div className="flex gap-2">
          <dt className="w-32 text-gray-400">Assigned To</dt>
          <dd>
            {match.assignedTo?.username ? (
              <a
                href={`/users/${getIDFromBase64(match.assignedTo.id, "UserType")}`}
                className="text-customGreen hover:underline"
              >
                {match.assignedTo.username}
              </a>
            ) : (
              "--"
            )}
          </dd>
        </div>

        <div className="flex gap-2">
          <dt className="w-32 text-gray-400">Result</dt>
          <dd>{match.result?.type || "--"}</dd>
        </div>

        <div className="flex gap-2">
          <dt className="w-32 text-gray-400">Winner</dt>
          <dd>
            {match.result?.winner ? (
              <a
                href={`/bots/${getIDFromBase64(
                  match.result.winner.id,
                  "BotType"
                )}`}
                className="text-customGreen hover:underline"
              >
                {match.result.winner.name}
              </a>
            ) : (
              "--"
            )}
          </dd>
        </div>

        <div className="flex gap-2">
          <dt className="w-32 text-gray-400">Duration</dt>
          <dd>{match.result?.gameTimeFormatted || "--"}</dd>
        </div>
        <div className="flex gap-2">
          <dt className="w-32 text-gray-400">Map</dt>
          <dd>
            {" "}
            <a href={`${match.map.downloadLink}`}>{match.map.name || "--"} </a>
          </dd>
        </div>
      </div>

      <div className="rounded-lg border border-neutral-700 bg-neutral-900/60 p-4 space-y-2 text-sm sm:text-base text-gray-200">
        <div className="flex gap-2">
          <dt className="w-32 text-gray-400">Origin</dt>
          <dd>
            {match.round?.competition.name
              ? "Competition"
              : match.requestedBy?.id
                ? "Match Request"
                : "Unknown"}
          </dd>
        </div>
        {match.round?.competition && (
          <>
            <div className="flex gap-2">
              <dt className="w-32 text-gray-400">Competition</dt>
              <dd>
                <a
                  href={`/competitions/${getIDFromBase64(match.round?.competition.id, "CompetitionType")}`}
                  className="text-customGreen hover:underline"
                >
                  {match.round?.competition.name}
                </a>
              </dd>
            </div>

            <div className="flex gap-2">
              <dt className="w-32 text-gray-400">Round</dt>
              <dd>
                <a
                  href={`/rounds/${getIDFromBase64(match.round?.id, "RoundType")}`}
                  className="text-customGreen hover:underline"
                >
                  {match.round?.number}
                </a>
              </dd>
            </div>
          </>
        )}
        {match.requestedBy && (
          <>
            <div className="flex gap-2">
              <dt className="w-32 text-gray-400">Requested By</dt>
              <dd>
                <a
                  href={`/authors/${getIDFromBase64(match.requestedBy.id, "UserType")}`}
                >
                  {match.requestedBy.username}
                </a>
              </dd>
            </div>
          </>
        )}
      </div>
    </div>
  );
}
