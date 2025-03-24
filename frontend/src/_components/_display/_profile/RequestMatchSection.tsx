import FilterableList from "../FilterableList";
import Link from "next/link";
import { formatDateISO } from "@/_lib/dateUtils";
import { graphql, useFragment } from "react-relay";
import { RequestMatchSection_viewer$key } from "./__generated__/RequestMatchSection_viewer.graphql";
import { getNodes } from "@/_lib/relayHelpers";

interface RequestMatchesSectionProps {
  viewer: RequestMatchSection_viewer$key;
}

export default function RequestMatchSection(props: RequestMatchesSectionProps) {
  const viewer = useFragment(
    graphql`
      fragment RequestMatchSection_viewer on ViewerType {
        requestMatchesLimit
        requestMatchesCountLeft
        requestedMatches {
          edges {
            node {
              id
              firstStarted
              participant1 {
                id
                name
              }
              participant2 {
                id
                name
              }
              result {
                type
                winner {
                  name
                }
              }
            }
          }
          totalCount
        }
        user {
          ownBots {
            edges {
              node {
                id
                ...ProfileBot_bot
              }
            }
          }
        }
      }
    `,
    props.viewer
  );

  const requestsUsed = viewer.requestedMatches?.totalCount;

  // const requestedMatches = useViewerRequestedMatches();

  const handleRequestNewMatch = () => {
    // Implement logic to request a new match via API
    // For example, you might open a modal or directly call an API endpoint.
    alert("Requesting a new match (placeholder)!");
  };

  return (
    <div id="matches" className="space-y-4">
      {/* Display request limit and requests left */}
      <div className="bg-gray-700 p-4 rounded-md flex flex-col sm:flex-row sm:justify-between sm:items-center space-y-2 sm:space-y-0">
        <div className="text-sm text-gray-300">
          <p className="text-left">
            <span className="font-bold">Requests used:</span>{" "}
            <span className="text-customGreen">
              {requestsUsed}/{viewer.requestMatchesLimit}
            </span>
          </p>
          <p className="text-left text-customGreen cursor-pointer">
            Increase Limit
          </p>
          {/* <p>
            <span className="font-bold">Match Request Limit:</span>{" "}
            <span className="text-customGreen">{matchRequestLimit}</span>
          </p>
          <p>
            <span className="font-bold">Requests Left:</span>{" "}
            <span className="text-customGreen">{requestsLeft}</span>
          </p> */}
        </div>
        <div>
          {/* Request new match button */}
          {/* If you have a custom button component `MainButton`, use that. Otherwise, use a standard button: */}
          <button
            onClick={handleRequestNewMatch}
            className="text-sm text-white bg-indigo-500 px-3 py-1 rounded-md hover:bg-indigo-400 transition"
          >
            Request New Match
          </button>
        </div>
      </div>
      <FilterableList
        data={getNodes(viewer.requestedMatches)}
        fields={[
          "id",
          "firstStarted",
          "participant1",
          "participant2",
          "result",
        ]} // Pass nested field as string
        defaultFieldSort={1}
        defaultSortOrder="desc"
        fieldLabels={{
          id: "Match ID",
          firstStarted: "Started",
          participant1: "Player 1",
          participant2: "Player 2",
          result: "Result",
        }}
        fieldClasses={
          {
            // "user.username": "hidden md:block",
            // type: "hidden sm:block",
          }
        }
        filters={[
          {
            type: "search",
            label: "Search",
            field: "all",
            placeholder: "Search all fields...",
          },
          {
            type: "dropdown",
            label: "Type",
            field: "type",
            placeholder: "Select type",
          },
        ]}
        renderRow={(item) => (
          <div className="block p-4 hover:bg-gray-800 rounded transition flex justify-between items-center shadow-md border border-gray-700">
            <div className="grid grid-cols-[repeat(auto-fit,_minmax(0,_1fr))]  w-full">
              <span className="text-left font-semibold text-gray-200 truncate">
                {item.id}
              </span>
              <span className="text-left text-gray-200  truncate">
                {formatDateISO(item.firstStarted)}
              </span>
              <Link href={`/bots/${item.participant1?.id}`}>
                <span className="bg-blue hidden sm:block text-left text-customGreen truncate ">
                  {item.participant1?.name || ""}
                </span>
              </Link>
              <Link href={`/bots/${item.participant2?.id}`}>
                <span className="bg-blue hidden sm:block text-left text-customGreen truncate ">
                  {item.participant2?.name || ""}
                </span>
              </Link>

              <span className="hidden md:block text-left text-gray-200  truncate">
                {item.result?.type}
              </span>
            </div>
          </div>
        )}
      />
      {/* In-Progress Matches */}
      {/* <div className="bg-gray-700 p-4 rounded-md space-y-3">
        <h3 className="text-lg font-semibold text-customGreen">In-Progress Requests</h3>
        {inProgressMatches.length > 0 ? (
          <ul className="space-y-2">
            {inProgressMatches.map((match) => (
              <li
                key={match.id}
                className="p-3 bg-gray-800 rounded-md border border-gray-600 text-gray-300 text-sm flex flex-col sm:flex-row sm:justify-between sm:items-center"
              >
                <span>
                  <span className="font-bold">Opponent:</span> {match.opponent}
                </span>
                <span className="text-xs text-gray-400 mt-1 sm:mt-0 sm:ml-2">{match.status}</span>
              </li>
            ))}
          </ul>
        ) : (
          <p className="text-gray-400 text-sm">No in-progress match requests.</p>
        )}
      </div> */}
    </div>
  );
}
