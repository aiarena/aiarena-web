import { formatDateISO } from "@/_lib/dateUtils";
import { graphql, useFragment } from "react-relay";
import { extractRelayID, getNodes } from "@/_lib/relayHelpers";
import FilterableList from "../_props/FilterableList";
import RequestMatchModal from "./_modals/RequestMatchModal";
import { useState } from "react";
import MainButton from "../_props/MainButton";
import WantMore from "../_display/WantMore";
import { UserMatchRequestsSection_viewer$key } from "./__generated__/UserMatchRequestsSection_viewer.graphql";
import { parseMatchResult } from "@/_lib/parseMatchResult";

interface UserMatchRequestsSectionProps {
  viewer: UserMatchRequestsSection_viewer$key;
}

export default function UserMatchRequestsSection(
  props: UserMatchRequestsSectionProps
) {
  const viewer = useFragment(
    graphql`
      fragment UserMatchRequestsSection_viewer on ViewerType {
        requestMatchesLimit
        requestMatchesCountLeft
        requestedMatches {
          edges {
            node {
              id
              started
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
              tags
              map {
                name
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
    <section className="h-full" aria-labelledby="match-requests-heading">
      <h2 id="match-requests-heading" className="sr-only">
        Match Requests
      </h2>
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
                aria-label={`${matchRequestsUsed} match requests used out of ${viewer.requestMatchesLimit} monthly limit. ${viewer.requestMatchesCountLeft} requests remaining.`}
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
            aria-label="Request a new match between bots"
            aria-describedby={
              viewer.requestMatchesCountLeft <= 0
                ? "no-requests-left"
                : undefined
            }
          />
        </div>
      </div>
      <div
        role="region"
        aria-labelledby="match-requests-table-heading"
        className="grow overflow-auto"
      >
        <h3 id="match-requests-table-heading" className="sr-only">
          Match Requests Table
        </h3>
        <FilterableList
          classes="mt-4 shadow-lg shadow-black bg-darken-2 backdrop-blur-sm"
          data={getNodes(viewer.requestedMatches)}
          hideMenu={true}
          fields={[
            "status",
            "id",
            "participant1.name",
            "participant2.name",
            "map.name",
            "tags",
            "started",
            "result.type",
          ]} // Pass nested field as string
          defaultFieldSort={0}
          defaultSortOrder="desc"
          fieldLabels={{
            status: "Status",
            id: "Match ID",
            "participant1.name": "Player 1",
            "participant2.name": "Player 2",
            "map.name": "Map",
            tags: "Tags",
            started: "Started",
            "result.type": "Result",
          }}
          fieldClasses={{
            status: "hidden md:flex",
            id: "hidden md:flex",
            "map.name": "hidden lg:flex",
            tags: "hidden lg:flex",
            started: "hidden sm:flex",
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
            <div className="block flex justify-between items-center" role="row">
              <div className="grid grid-cols-[repeat(auto-fit,_minmax(0,_1fr))] w-full">
                <p
                  className="pl-2 hidden md:flex text-left text-gray-200 truncate"
                  role="cell"
                  aria-label={`Match status: ${match.status}`}
                >
                  {match.status}
                </p>
                <a
                  className="pl-2 hidden md:flex text-left font-semibold text-gray-200 truncate focus:outline-none focus:ring-2 focus:ring-customGreen focus:ring-opacity-50"
                  href={`/matches/${extractRelayID(match.id, "MatchType")}`}
                  role="cell"
                  aria-label={`View match details for match ID ${match.id}`}
                >
                  {extractRelayID(match.id, "MatchType")}
                </a>

                <a
                  className="pl-2 text-left text-customGreen truncate focus:outline-none focus:ring-2 focus:ring-customGreen focus:ring-opacity-50"
                  href={`/bots/${extractRelayID(match.participant1?.id, "BotType")}`}
                  role="cell"
                  aria-label={`View bot profile for ${match.participant1?.name}, participant 1`}
                >
                  {match.participant1?.name}
                </a>
                <a
                  className="pl-2 text-left text-customGreen truncate focus:outline-none focus:ring-2 focus:ring-customGreen focus:ring-opacity-50"
                  href={`/bots/${extractRelayID(match.participant2?.id, "BotType")}`}
                  role="cell"
                  aria-label={`View bot profile for ${match.participant2?.name}, participant 2`}
                >
                  {match.participant2?.name}
                </a>
                <p
                  className="pl-2 text-left hidden lg:flex text-gray-200 truncate"
                  role="cell"
                  aria-label={`Map: ${match.map.name}`}
                >
                  {match.map.name}
                </p>
                <p
                  className="pl-2 text-left hidden lg:flex text-gray-200 truncate"
                  role="cell"
                  aria-label={`Tags: ${match.tags}`}
                >
                  {match.tags && match.tags.join(", ")}
                </p>
                <p
                  className="pl-2 hidden sm:flex text-left text-gray-200 truncate"
                  role="cell"
                  aria-label={`Match started: ${match.status !== "Queued" && match.started ? formatDateISO(match.started) : "Not yet started"}`}
                >
                  {match.status !== "Queued"
                    ? formatDateISO(match.firstStarted)
                    : ""}
                </p>
                <p
                  className="pl-2 text-left text-gray-200 truncate"
                  role="cell"
                  aria-label={`Match result: ${match.result?.type || "No result yet"}`}
                >
                  {parseMatchResult(
                    match.result?.type,
                    match.participant1?.name,
                    match.participant2?.name
                  )}
                </p>
              </div>
            </div>
          )}
          aria-label={`Table of ${getNodes(viewer.requestedMatches).length} match requests`}
        />
      </div>

      <RequestMatchModal
        isOpen={isRequestMatchModalOpen}
        onClose={() => setIsRequestMatchModalOpen(false)}
      />
    </section>
  );
}
