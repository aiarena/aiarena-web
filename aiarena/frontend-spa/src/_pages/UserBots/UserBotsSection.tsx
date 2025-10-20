import React, { Suspense, useState } from "react";

import { graphql, useFragment } from "react-relay";
import UploadBotModal from "./UserBotsSection/_modals/UploadBotModal";

import { UserBotsSection_viewer$key } from "./__generated__/UserBotsSection_viewer.graphql";

import UserBotsList from "./UserBotsSection/UserBotsList";

import clsx from "clsx";
import WantMore from "@/_components/_display/WantMore";
import Dropdown from "@/_components/_actions/Dropdown";
import DropdownButton from "@/_components/_actions/DropdownButton";
import Searchbar from "@/_components/_actions/Searchbar";
import MainButton from "@/_components/_actions/MainButton";
import LoadingSpinner from "@/_components/_display/LoadingSpinnerGray";

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
          bots(first: 20) {
            totalCount
          }
        }
      }
    `,
    props.viewer,
  );

  const [isUploadBotModalOpen, setUploadBotModalOpen] = useState(false);
  const [searchBarValue, setSearchBarValue] = useState("");
  const [orderBy, setOrderBy] = useState({ display: "Order By", value: "" });

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
                    "text-yellow-500",
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
          {viewer.user?.bots?.totalCount &&
          viewer.user?.bots?.totalCount >= 1 ? (
            <>
              <Dropdown title={orderBy.display}>
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
                value={searchBarValue}
                onChange={setSearchBarValue}
                placeholder="Search your bots..."
                aria-label="Search bots by name"
              />
            </>
          ) : null}
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
