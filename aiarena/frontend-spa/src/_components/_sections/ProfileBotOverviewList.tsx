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
        ownBots {
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

  const activeBotParticipation = getNodes(userData?.ownBots).reduce(
    (total, item) => {
      const activeCount =
        getNodes(item.competitionParticipations).filter(
          (participation) => participation.active
        ).length || 0;
      return total + activeCount;
    },
    0
  );

  const [useSort, setUseSort] = useState("Sort By");
  const [searchBarValue, setSearchBarValue] = useState("");

  return (
    <div className="bg-customBackgroundColor1">
      <div className="flex justify-between  flex-wrap-reverse w-full pb-4">
        <div className="flex gap-2 flex-wrap">
          {viewer.activeBotsLimit ? (
            <div className="block">
              <p className="pb-1">
                {activeBotParticipation} / {viewer.activeBotsLimit} active
                competition participations.
              </p>
              <p>
                Want more? Consider{" "}
                <a
                  className="cursor-pointer"
                  href={"https://www.patreon.com/aiarena"}
                >
                  supporting us
                </a>
                .
              </p>
            </div>
          ) : null}
        </div>

        <div className="flex gap-4 ">
          <Dropdown title={useSort}>
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
        {getNodes(userData?.ownBots)
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
                return (a.competitionParticipations?.edges?.length || 0) <=
                  (b.competitionParticipations?.edges?.length || 0)
                  ? 0
                  : -1;

              default:
                if (searchBarValue.trim().length > 0) {
                  const pattern = searchBarValue?.trim();

                  const regex = new RegExp(pattern, "i");
                  const aMatches = regex.test(a.name) ? 0 : -1;
                  const bMatches = regex.test(b.name) ? 0 : -1;

                  return bMatches - aMatches;
                } else if (activeBotParticipation == 0) {
                  return a.botZipUpdated <= b.botZipUpdated ? 0 : -1;
                } else {
                  return (a.competitionParticipations?.edges?.length || 0) <=
                    (b.competitionParticipations?.edges?.length || 0)
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
