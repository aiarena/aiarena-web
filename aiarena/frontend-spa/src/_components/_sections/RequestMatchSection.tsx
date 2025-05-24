import { formatDateISO } from "@/_lib/dateUtils";
import { graphql, useFragment } from "react-relay";
import { RequestMatchSection_viewer$key } from "./__generated__/RequestMatchSection_viewer.graphql";
import { extractRelayID, getNodes } from "@/_lib/relayHelpers";
import FilterableList from "../_props/FilterableList";
import RequestMatchModal from "./_modals/RequestMatchModal";
import { useState } from "react";
import MainButton from "../_props/MainButton";
import WantMore from "../_display/WantMore";

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
              status
            }
          }
          totalCount
        }
      }
    `,
    props.viewer
  );
  const [isRequestMatchModalOpen, setIsRequestMatchModalOpen] = useState(false);
  const matchRequestsUsed =
    viewer.requestMatchesLimit - viewer.requestMatchesCountLeft;

  return (
    <div className="h-full]">
      <div className="flex flex-wrap-reverse w-fullitems-start">
        {/* Display request limit and requests left */}
        <div className="flex gap-4 flex-wrap pb-4">
          <div className="block">
            <p className="pb-1">
              <span
                className={`
                  
                  ${viewer.requestMatchesCountLeft <= 5 && viewer.requestMatchesCountLeft > 0 ? "text-yellow-500" : ""}
                  ${viewer.requestMatchesCountLeft <= 0 ? "text-red-400" : ""}
                  `}
              >
                {" "}
                {matchRequestsUsed}
              </span>{" "}
              / {viewer.requestMatchesLimit} monthly match requests used.
            </p>
            <WantMore />
          </div>
        </div>

        <div className="flex gap-4 ml-auto ">
          <MainButton
            onClick={() => setIsRequestMatchModalOpen(true)}
            text="Request New Match"
          />
        </div>
      </div>

      <FilterableList
        classes="mt-4 shadow-lg shadow-black bg-darken-2"
        data={getNodes(viewer.requestedMatches)}
        hideMenu={true}
        fields={[
          "status",
          "id",

          "participant1.name",
          "participant2.name",
          "firstStarted",
          "result.type",
        ]} // Pass nested field as string
        defaultFieldSort={0}
        defaultSortOrder="desc"
        fieldLabels={{
          status: "Status",
          id: "Match ID",
          "participant1.name": "Player 1",
          "participant2.name": "Player 2",
          firstStarted: "Started",
          "result.type": "Result",
        }}
        fieldClasses={{
          status: "hidden md:flex",
          id: "hidden md:flex",
          firstStarted: "hidden sm:flex",
        }}
        filters={[
          {
            type: "search",
            label: "Search",
            field: "all",
            placeholder: "Search all fields...",
          },
        ]}
        renderRow={(match) => (
          <div className="block flex justify-between items-center ">
            <div className="grid grid-cols-[repeat(auto-fit,_minmax(0,_1fr))]  w-full">
              <p className="pl-2 hidden md:flex text-left text-gray-200  truncate">
                {match.status}
              </p>
              <a
                className="pl-2 hidden md:flex text-left font-semibold text-gray-200 truncate"
                href={`/matches/${extractRelayID(match.id, "MatchType")}`}
              >
                {match.id}
              </a>

              <a
                className="pl-2 text-left text-customGreen truncate "
                href={`/bots/${extractRelayID(match.participant1?.id, "BotType")}`}
              >
                {match.participant1?.name}
              </a>
              <a
                className="pl-2 text-left text-customGreen truncate "
                href={`/bots/${extractRelayID(match.participant2?.id, "BotType")}`}
              >
                {match.participant2?.name}
              </a>
              <p className="pl-2 hidden sm:flex text-left text-gray-200  truncate">
                {match.status != "Queued"
                  ? formatDateISO(match.firstStarted)
                  : ""}
              </p>
              <p className="pl-2 text-left text-gray-200  truncate">
                {match.result?.type}
              </p>
            </div>
          </div>
        )}
      />

      <RequestMatchModal
        isOpen={isRequestMatchModalOpen}
        onClose={() => setIsRequestMatchModalOpen(false)}
      />
    </div>
  );
}
