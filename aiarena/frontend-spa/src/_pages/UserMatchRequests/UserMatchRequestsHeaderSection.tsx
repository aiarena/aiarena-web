import { Suspense, useState } from "react";

import { graphql, useFragment } from "react-relay";
import clsx from "clsx";

import { UserMatchRequestsHeaderSection_viewer$key } from "./__generated__/UserMatchRequestsHeaderSection_viewer.graphql";
import LoadingDots from "@/_components/_display/LoadingDots";
import WatchYourGamesButton from "@/_components/_actions/WatchYourGamesButton";
import WantMore from "@/_components/_display/WantMore";
import MainButton from "@/_components/_actions/MainButton";
import RequestMatchModal from "./UserMatchRequests/_modals/RequestMatchModal";
import WatchGamesModal from "./UserMatchRequests/_modals/WatchGamesModal";

type UserMatchRequestsHeaderSectionProps = {
  viewer: UserMatchRequestsHeaderSection_viewer$key;
};

export default function UserMatchRequestsHeaderSection(
  props: UserMatchRequestsHeaderSectionProps,
) {
  const [isRequestMatchModalOpen, setIsRequestMatchModalOpen] = useState(false);
  const [isWatchYourGamesModalOpen, setIsWatchYourGamesModalOpen] =
    useState(false);

  const viewer = useFragment(
    graphql`
      fragment UserMatchRequestsHeaderSection_viewer on Viewer {
        requestMatchesLimit
        requestMatchesCountLeft
      }
    `,
    props.viewer,
  );

  const matchRequestsUsed =
    viewer.requestMatchesLimit - viewer.requestMatchesCountLeft;

  return (
    <div className="flex flex-wrap-reverse w-fullitems-start">
      {/* Display request limit and requests left */}
      <Suspense fallback={<LoadingDots />}>
        <div className="flex gap-4 flex-wrap pb-4">
          <div className="block">
            <p className="pb-1">
              <span
                className={clsx(
                  viewer.requestMatchesCountLeft <= 5 &&
                    viewer.requestMatchesCountLeft > 0 &&
                    "text-yellow-500",
                  viewer.requestMatchesCountLeft <= 0 && "text-red-400",
                )}
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
      </Suspense>
      <div className="flex gap-4 ml-auto ">
        <div>
          <WatchYourGamesButton
            onClick={() => setIsWatchYourGamesModalOpen(true)}
          >
            <span>Watch Your Games</span>
          </WatchYourGamesButton>
        </div>
        <MainButton
          onClick={() => setIsRequestMatchModalOpen(true)}
          text="Request New Match"
          aria-label="Request a new match between Bots"
          aria-describedby={
            viewer.requestMatchesCountLeft <= 0 ? "no-requests-left" : undefined
          }
        />
      </div>
      <RequestMatchModal
        isOpen={isRequestMatchModalOpen}
        onClose={() => setIsRequestMatchModalOpen(false)}
      />

      <WatchGamesModal
        isOpen={isWatchYourGamesModalOpen}
        onClose={() => setIsWatchYourGamesModalOpen(false)}
      />
    </div>
  );
}
