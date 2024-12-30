import { useState } from "react";
import internal from "stream";
// import MainButton from "../_props/MainButton"; // If you have a custom button component
// If not, just use a <button> with Tailwind classes.




interface RequestMatchesSectionProps {
  requestMatchesCountLeft?: number;
  requestMatchesLimit?: number;
}


export default function RequestMatchesSection({requestMatchesCountLeft, requestMatchesLimit} : RequestMatchesSectionProps) {
  // Example state - replace with real data fetching logic
  const [matchRequestLimit, setMatchRequestLimit] = useState(requestMatchesLimit || 0);
  const [requestsRemaining, setRequestsUsed] = useState(requestMatchesCountLeft || 0);
  const [inProgressMatches, setInProgressMatches] = useState([
    { id: 1, opponent: "BotA", status: "Match scheduled for tomorrow" },
    { id: 2, opponent: "BotB", status: "Processing..." },
  ]);

  const requestsUsed = matchRequestLimit - requestsRemaining;

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
            <span className="text-customGreen">{requestsUsed}/{matchRequestLimit}</span>
           
          </p>
          <p className="text-left text-customGreen cursor-pointer">Increase Limit</p>
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

      {/* In-Progress Matches */}
      <div className="bg-gray-700 p-4 rounded-md space-y-3">
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
      </div>
    </div>
  );
}
