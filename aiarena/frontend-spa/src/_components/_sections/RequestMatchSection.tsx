import { formatDateISO } from "@/_lib/dateUtils";
import { graphql, useFragment } from "react-relay";
import { RequestMatchSection_viewer$key } from "./__generated__/RequestMatchSection_viewer.graphql";
import { extractRelayID, getNodes } from "@/_lib/relayHelpers";
import FilterableList from "../_props/FilterableList";
import RequestMatchModal from "./_modals/RequestMatchModal";
import { useState } from "react";
import MainButton from "../_props/MainButton";

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

  const [isRequestMatchModalOpen, setIsRequestMatchModalOpen] = useState(false);

  return (
    <div id="matches">
      {/* Display request limit and requests left */}
      <div className="bg-gray-700 p-4 rounded-md flex flex-col sm:flex-row sm:justify-between sm:items-center space-y-2 sm:space-y-0">
        <div className="text-sm text-gray-300">
          <div className="text-left flex">
            <p className="font-bold">Requests remaining:</p>
            <div className="flex">
              <p className="text-customGreen ml-1">
                {viewer.requestMatchesCountLeft}
              </p>
              <p>/{viewer.requestMatchesLimit}</p>
            </div>
          </div>
          <p className="text-left text-customGreen cursor-pointer">
            Increase Limit
          </p>
        </div>
        <div>
          <MainButton
            onClick={() => setIsRequestMatchModalOpen(true)}
            text="Request New Match"
          />
        </div>
      </div>
      <FilterableList
        classes="pt-4"
        data={getNodes(viewer.requestedMatches)}
        fields={[
          "id",
          "firstStarted",
          "participant1.name",
          "participant2.name",
          "result.type",
        ]} // Pass nested field as string
        defaultFieldSort={1}
        defaultSortOrder="desc"
        fieldLabels={{
          id: "Match ID",
          firstStarted: "Started",
          "participant1.name": "Player 1",
          "participant2.name": "Player 2",
          "result.type": "Result",
        }}
        fieldClasses={{
          id: "hidden md:block",
          firstStarted: "hidden sm:block",
        }}
        filters={[
          {
            type: "search",
            label: "Search",
            field: "all",
            placeholder: "Search all fields...",
          },
        ]}
        renderRow={(item) => (
          <div className="block p-4 hover:bg-gray-800 bg-gray-900 rounded transition flex justify-between items-center shadow-md border border-gray-700">
            <div className="grid grid-cols-[repeat(auto-fit,_minmax(0,_1fr))]  w-full">
              <a
                className=" hidden md:block text-left font-semibold text-gray-200 truncate"
                href={`/matches/${extractRelayID(item.id, "MatchType")}`}
              >
                {extractRelayID(item.id, "MatchType")}
              </a>

              <p className="hidden sm:block text-left text-gray-200  truncate">
                {item.firstStarted != undefined
                  ? formatDateISO(item.firstStarted)
                  : "In Queue"}
              </p>
              <a
                className=" text-left text-customGreen truncate "
                href={`/bots/${extractRelayID(item.participant1?.id, "BotType")}`}
              >
                {item.participant1?.name || ""}
              </a>
              <a
                className=" text-left text-customGreen truncate "
                href={`/bots/${extractRelayID(item.participant2?.id, "BotType")}`}
              >
                {item.participant2?.name || ""}
              </a>

              <p className=" text-left text-gray-200  truncate">
                {item.result?.type}
              </p>
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
      <RequestMatchModal
        isOpen={isRequestMatchModalOpen}
        onClose={() => setIsRequestMatchModalOpen(false)}
      />
    </div>
  );
}
