import React, { Suspense, useState } from "react";

import { graphql, useFragment } from "react-relay";
import MainButton from "../_actions/MainButton";
import UploadBotModal from "./UserBotsSection/_modals/UploadBotModal";

import Searchbar from "../_actions/Searchbar";
import Dropdown from "../_actions/Dropdown";
import DropdownButton from "../_actions/DropdownButton";
import WantMore from "../_display/WantMore";
import { UserBotsSection_viewer$key } from "./__generated__/UserBotsSection_viewer.graphql";

import UserBotsList from "./UserBotsSection/UserBotsList";
import LoadingSpinner from "../_display/LoadingSpinnerGray";
import clsx from "clsx";

interface UserBotsSectionProps {
  viewer: UserBotsSection_viewer$key;
}

export const UserBotsSection: React.FC<UserBotsSectionProps> = (props) => {
  const viewer = useFragment(
    graphql`
      fragment UserBotsSection_viewer on Viewer {
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
  const [searchBarValue, setSearchBarValue] = useState("");
  const [orderBy, setOrderBy] = useState({ display: "Order By", value: "" });
  const [filterLoading, setFilterLoading] = useState(false);

  return (
    <section aria-labelledby="user-bots-heading">
      <div className="flex flex-wrap-reverse w-fullitems-start">
        {/* Display active competition limit and current active competitions */}
        <div className="flex gap-4 flex-wrap pb-4">
          <div className="block">
            {/*  Below section can also be deffered with Relay 19.0 */}
            <p className="pb-1">
              <span
                className={clsx(
                  "pb-1",
                  viewer.activeBotParticipations ===
                    viewer.activeBotParticipationLimit && "text-red-400",
                  viewer.activeBotParticipationLimit &&
                    viewer.activeBotParticipations &&
                    viewer.activeBotParticipationLimit -
                      viewer.activeBotParticipations ===
                      1 &&
                    "text-yellow-500"
                )}
              >
                {viewer.activeBotParticipations}
              </span>{" "}
              / {viewer.activeBotParticipationLimit} active competition
              participations.
            </p>
            <WantMore />
          </div>
        </div>
        <div
          className="flex gap-4 ml-auto"
          role="group"
          aria-label="Bot filtering and sorting controls"
        >
          <Dropdown title={orderBy.display} isLoading={filterLoading}>
            <DropdownButton
              onClick={() =>
                setOrderBy({
                  display: "Active Participations",
                  value: "-total_active_competition_participations",
                })
              }
              title={"Active Participations"}
            />

            <DropdownButton
              onClick={() =>
                setOrderBy({
                  display: "Last Zip Updated",
                  value: "-bot_zip_updated",
                })
              }
              title={"Last Zip Updated"}
            />
            <DropdownButton
              onClick={() =>
                setOrderBy({
                  display: "First Created",
                  value: "created",
                })
              }
              title={"First Created"}
            />
          </Dropdown>
          <Searchbar
            onChange={(e) => {
              setSearchBarValue(e.target.value);
            }}
            isLoading={filterLoading}
            value={searchBarValue}
            placeholder="Search your bots..."
            aria-label="Search bots by name"
          />

          <div role="group" aria-label="Bot actions">
            <div className="hidden md:block">
              <MainButton
                onClick={() => setUploadBotModalOpen(true)}
                text="Upload Bot"
                aria-label="Upload a new bot"
              />
            </div>
            <div className="block md:hidden">
              <MainButton
                onClick={() => setUploadBotModalOpen(true)}
                text="+"
                aria-label="Upload a new bot"
              />
            </div>
          </div>
        </div>
      </div>

      <Suspense fallback={<LoadingSpinner color="light-gray" />}>
        {viewer.user ? (
          <UserBotsList
            user={viewer.user}
            searchBarValue={searchBarValue}
            orderBy={orderBy.value}
            onLoadingChange={setFilterLoading}
          />
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
