import { useState } from "react";
import WantMore from "../_display/WantMore";
import MainButton from "../_props/MainButton";
import { graphql, useFragment } from "react-relay";

import RequestMatchModal from "./_modals/RequestMatchModal";
import { UserMatchRequestsHeaderSection_viewer$key } from "./__generated__/UserMatchRequestsHeaderSection_viewer.graphql";

type UserMatchRequestsHeaaderSectionProps = {
  viewer: UserMatchRequestsHeaderSection_viewer$key;
};

export default function UserMatchRequestsHeaderSection(
  props: UserMatchRequestsHeaaderSectionProps
) {
  const [isRequestMatchModalOpen, setIsRequestMatchModalOpen] = useState(false);

  const viewer = useFragment(
    graphql`
      fragment UserMatchRequestsHeaderSection_viewer on Viewer {
        requestMatchesLimit
        requestMatchesCountLeft
      }
    `,
    props.viewer
  );

  const matchRequestsUsed =
    viewer.requestMatchesLimit - viewer.requestMatchesCountLeft;

  return (
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
            viewer.requestMatchesCountLeft <= 0 ? "no-requests-left" : undefined
          }
        />
      </div>
      <RequestMatchModal
        isOpen={isRequestMatchModalOpen}
        onClose={() => setIsRequestMatchModalOpen(false)}
      />
    </div>
  );
}
