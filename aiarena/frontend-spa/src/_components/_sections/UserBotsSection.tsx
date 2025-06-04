import React, { Suspense, useState } from "react";

import { graphql, useFragment } from "react-relay";
import MainButton from "../_props/MainButton";
import UploadBotModal from "./_modals/UploadBotModal";

import Searchbar from "../_props/Searchbar";
// import Dropdown from "../_props/Dropdown";
// import DropdownButton from "../_props/DropdownButton";
import WantMore from "../_display/WantMore";
import { UserBotsSection_viewer$key } from "./__generated__/UserBotsSection_viewer.graphql";

import UserBotsList from "./UserBotsList";
import LoadingSpinner from "../_display/LoadingSpinnerGray";

interface UserBotsSectionProps {
  viewer: UserBotsSection_viewer$key;
}

export const UserBotsSection: React.FC<UserBotsSectionProps> = (props) => {
  const viewer = useFragment(
    graphql`
      fragment UserBotsSection_viewer on ViewerType {
        activeBotParticipations
        activeBotParticipationLimit

        user {
          ...UserBotsList_user
        }
      }
    `,
    props.viewer
  );

  const [isUploadBotModalOpen, setUploadBotModalOpen] = useState(false);
  // const [useSort, setUseSort] = useState("");
  const [searchBarValue, setSearchBarValue] = useState("");

  return (
    <section aria-labelledby="user-bots-heading">
      <div className="flex flex-wrap-reverse w-fullitems-start">
        {/* Display active competition limit and current active competitions */}
        <div className="flex gap-4 flex-wrap pb-4">
          <div className="block">
            {/*  Below section can also be deffered with Relay 19.0 */}
            <p className="pb-1 ">
              <span
                className={`pb-1 ${viewer.activeBotParticipations == viewer.activeBotParticipationLimit ? "text-red-400" : ""}
                   ${viewer.activeBotParticipationLimit && viewer.activeBotParticipations && viewer.activeBotParticipationLimit - viewer.activeBotParticipations == 1 ? "text-yellow-500" : ""}
                   `}
              >
                {viewer.activeBotParticipations}
              </span>{" "}
              / {viewer.activeBotParticipationLimit} {""}
              active competition participations.
            </p>
            <WantMore />
          </div>
        </div>
        <div
          className="flex gap-4 ml-auto "
          role="group"
          aria-label="Agent filtering and sorting controls"
        >
          {/* <Dropdown title={useSort}>
            <DropdownButton
              onClick={() => setUseSort("Active Competitions")}
              title={"Active Competitions"}
            />

            <DropdownButton
              onClick={() => setUseSort("Zip Updated")}
              title={"Zip Updated"}
            />
            <DropdownButton
              onClick={() => setUseSort("Created")}
              title={"Created"}
            />

            <DropdownButton
              onClick={() => setUseSort("Trophies")}
              title={"Trophies"}
            />
          </Dropdown> */}

          <Searchbar
            onChange={(e) => {
              setSearchBarValue(e.target.value);
              // setUseSort("Sort By");
            }}
            value={searchBarValue}
            placeholder="Search your Agents..."
            aria-label="Search Agents by name"
          />

          <div role="group" aria-label="Agent actions">
            <div className="hidden md:block">
              <MainButton
                onClick={() => setUploadBotModalOpen(true)}
                text="Upload Agent"
                aria-label="Upload a new Agent"
              />
            </div>
            <div className="block md:hidden">
              <MainButton
                onClick={() => setUploadBotModalOpen(true)}
                text="+"
                aria-label="Upload a new Agent"
              />
            </div>
          </div>
        </div>
      </div>
      <Suspense fallback={<LoadingSpinner color="light-gray" />}>
        {viewer.user ? (
          <UserBotsList user={viewer.user} searchBarValue={searchBarValue} />
        ) : (
          <></>
        )}
      </Suspense>
      <UploadBotModal
        isOpen={isUploadBotModalOpen}
        onClose={() => setUploadBotModalOpen(false)}
        aria-labelledby="upload-bot-modal-title"
        aria-describedby="upload-bot-modal-description"
      />
    </section>
  );
};
