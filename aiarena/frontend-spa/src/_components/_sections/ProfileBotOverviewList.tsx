import React, { useState } from "react";

import { graphql, useFragment } from "react-relay";
import { ProfileBotOverviewList_viewer$key } from "./__generated__/ProfileBotOverviewList_viewer.graphql";
import { getNodes } from "@/_lib/relayHelpers";
import MainButton from "../_props/MainButton";
import UploadBotModal from "./_modals/UploadBotModal";
import ProfileBot from "./ProfileBot";
import { ProfileBotOverviewList_user$key } from "./__generated__/ProfileBotOverviewList_user.graphql";
import Searchbar from "../_props/Searchbar";
import Dropdown from "../_props/Dropdown";
import DropdownButton from "../_props/DropdownButton";
import WantMore from "../_display/WantMore";

interface ProfileBotOverviewListProps {
  viewer: ProfileBotOverviewList_viewer$key;
}

export const ProfileBotOverviewList: React.FC<ProfileBotOverviewListProps> = (
  props
) => {
  const viewer = useFragment(
    graphql`
      fragment ProfileBotOverviewList_viewer on ViewerType {
        activeBotsLimit
        user {
          ...ProfileBotOverviewList_user
        }
      }
    `,
    props.viewer
  );

  const userData = useFragment(
    graphql`
      fragment ProfileBotOverviewList_user on UserType {
        bots {
          edges {
            node {
              id
              botZipUpdated
              created
              name
              trophies {
                edges {
                  node {
                    id
                  }
                }
              }
              competitionParticipations {
                edges {
                  node {
                    active
                  }
                }
              }
              ...ProfileBot_bot
            }
          }
        }
      }
    `,
    viewer.user as ProfileBotOverviewList_user$key
  );

  const [isUploadBotModalOpen, setUploadBotModalOpen] = useState(false);

  const activeBotParticipations = getNodes(userData?.bots).reduce(
    (total, item) => {
      const activeCount =
        getNodes(item.competitionParticipations).filter(
          (participation) => participation.active
        ).length || 0;
      return total + activeCount;
    },
    0
  );

  const totalTrophies = getNodes(userData?.bots).reduce((total, item) => {
    const trophyCount = getNodes(item.trophies).length || 0;
    return total + trophyCount;
  }, 0);

  const [useSort, setUseSort] = useState("Sort By");

  const [searchBarValue, setSearchBarValue] = useState("");

  return (
    <div className="bg-customBackgroundColor1">
      <div className="flex flex-wrap-reverse w-fullitems-start">
        {/* Display active competition limit and current active competitions */}
        <div className="flex gap-4 flex-wrap pb-4">
          <div className="block">
            <p className="pb-1 ">
              <span
                className={`pb-1 ${activeBotParticipations == viewer.activeBotsLimit ? "text-red-400" : ""}
                   ${viewer.activeBotsLimit && viewer.activeBotsLimit - activeBotParticipations == 1 ? "text-yellow-500" : ""}
                   `}
              >
                {activeBotParticipations}
              </span>{" "}
              / {viewer.activeBotsLimit} {""}
              active competition participations.
            </p>
            <WantMore />
          </div>
        </div>
        <div className="flex gap-4 ml-auto ">
          <Dropdown title={useSort}>
            {activeBotParticipations > 0 ? (
              <DropdownButton
                onClick={() => setUseSort("Active Competitions")}
                title={"Active Competitions"}
              />
            ) : (
              <></>
            )}
            <DropdownButton
              onClick={() => setUseSort("Zip Updated")}
              title={"Zip Updated"}
            />
            <DropdownButton
              onClick={() => setUseSort("Created")}
              title={"Created"}
            />
            {totalTrophies > 0 ? (
              <DropdownButton
                onClick={() => setUseSort("Trophies")}
                title={"Trophies"}
              />
            ) : (
              <></>
            )}
          </Dropdown>

          <Searchbar
            onChange={(e) => {
              setSearchBarValue(e.target.value);
              setUseSort("Sort By");
            }}
            value={searchBarValue}
            placeholder="Search your bots..."
          />

          <div>
            <div className="hidden md:block">
              <MainButton
                onClick={() => setUploadBotModalOpen(true)}
                text="Upload Bot"
              />
            </div>
            <div className="block md:hidden">
              <MainButton
                onClick={() => setUploadBotModalOpen(true)}
                text="+"
              />
            </div>
          </div>
        </div>
      </div>

      <ul className="space-y-12">
        {getNodes(userData?.bots)
          .sort((a, b) => {
            switch (useSort) {
              case "Zip Updated":
                return a.botZipUpdated <= b.botZipUpdated ? 0 : -1;
              case "Created":
                return a.created <= b.created ? 0 : -1;
              case "Trophies":
                return (a.trophies?.edges?.length || 0) <=
                  (b.trophies?.edges?.length || 0)
                  ? 0
                  : -1;
              case "Active Competitions":
                return (a.competitionParticipations?.edges?.filter(
                  (comp) => comp?.node?.active == true
                ).length || 0) <=
                  (b.competitionParticipations?.edges.filter(
                    (comp) => comp?.node?.active == true
                  ).length || 0)
                  ? 0
                  : -1;

              default:
                if (searchBarValue.trim().length > 0) {
                  const pattern = searchBarValue?.trim();

                  const regex = new RegExp(pattern, "i");
                  const aMatches = regex.test(a.name) ? 0 : -1;
                  const bMatches = regex.test(b.name) ? 0 : -1;

                  return bMatches - aMatches;
                } else if (activeBotParticipations == 0) {
                  return a.botZipUpdated <= b.botZipUpdated ? 0 : -1;
                } else {
                  return (a.competitionParticipations?.edges?.filter(
                    (comp) => comp?.node?.active == true
                  ).length || 0) <=
                    (b.competitionParticipations?.edges.filter(
                      (comp) => comp?.node?.active == true
                    ).length || 0)
                    ? 0
                    : -1;
                }
            }
          })
          .map((bot) => (
            <li key={bot.id}>
              <ProfileBot bot={bot} />
            </li>
          ))}
      </ul>
      <UploadBotModal
        isOpen={isUploadBotModalOpen}
        onClose={() => setUploadBotModalOpen(false)}
      />
    </div>
  );
};
