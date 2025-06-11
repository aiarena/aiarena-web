import { graphql, useFragment } from "react-relay";
import RequestMatchModal from "./_modals/RequestMatchModal";
import { Suspense, useState } from "react";
import MainButton from "../_props/MainButton";
import WantMore from "../_display/WantMore";
import { UserMatchRequestsSection_viewer$key } from "./__generated__/UserMatchRequestsSection_viewer.graphql";
import MatchRequestsTable from "../_props/MatchRequestsTable";
import LoadingSpinner from "../_display/LoadingSpinnerGray";

interface UserMatchRequestsSectionProps {
  viewer: UserMatchRequestsSection_viewer$key;
}

export default function UserMatchRequestsSection(
  props: UserMatchRequestsSectionProps
) {
  const viewer = useFragment(
    graphql`
      fragment UserMatchRequestsSection_viewer on Viewer {
        requestMatchesLimit
        requestMatchesCountLeft
        ...MatchRequestsTable_viewer
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
            aria-label="Request a new match between Agents"
            aria-describedby={
              viewer.requestMatchesCountLeft <= 0
                ? "no-requests-left"
                : undefined
            }
          />
        </div>
      </div>
      <div role="region" aria-labelledby="match-requests-table-heading">
        <h3 id="match-requests-table-heading" className="sr-only">
          Match Requests Table
        </h3>
        <Suspense fallback={<LoadingSpinner />}>
          <MatchRequestsTable viewer={viewer} />
        </Suspense>
      </div>

      <RequestMatchModal
        isOpen={isRequestMatchModalOpen}
        onClose={() => setIsRequestMatchModalOpen(false)}
      />
    </section>
  );
}
