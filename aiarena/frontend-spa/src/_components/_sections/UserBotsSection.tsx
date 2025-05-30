import React, { useState } from "react";

import { graphql, useFragment } from "react-relay";
import { getNodes } from "@/_lib/relayHelpers";
import MainButton from "../_props/MainButton";
import UploadBotModal from "./_modals/UploadBotModal";

import Searchbar from "../_props/Searchbar";
import Dropdown from "../_props/Dropdown";
import DropdownButton from "../_props/DropdownButton";
import WantMore from "../_display/WantMore";
import { UserBotsSection_viewer$key } from "./__generated__/UserBotsSection_viewer.graphql";
import { UserBotsSection_user$key } from "./__generated__/UserBotsSection_user.graphql";
import UserBot from "../_display/userbot/UserBot";

interface UserBotsSectionProps {
  viewer: UserBotsSection_viewer$key;
}

export const UserBotsSection: React.FC<UserBotsSectionProps> = (props) => {
  const viewer = useFragment(
    graphql`
      fragment UserBotsSection_viewer on ViewerType {
        activeBotsLimit
        user {
          ...UserBotsSection_user
        }
      }
    `,
    props.viewer
  );

  const userData = useFragment(
    graphql`
      fragment UserBotsSection_user on UserType {
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
              ...UserBot_bot
            }
          }
        }
      }
    `,
    viewer.user as UserBotsSection_user$key
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
    <section aria-labelledby="user-bots-heading">
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
        <div
          className="flex gap-4 ml-auto "
          role="group"
          aria-label="Bot filtering and sorting controls"
        >
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
      <div role="region" aria-labelledby="bots-list-heading" aria-live="polite">
        <h2 id="bots-list-heading" className="sr-only">
          Your Bots List
        </h2>
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
              <li key={bot.id} id={bot.id} role="listitem">
                <UserBot bot={bot} />
              </li>
            ))}
        </ul>
      </div>
      <UploadBotModal
        isOpen={isUploadBotModalOpen}
        onClose={() => setUploadBotModalOpen(false)}
        aria-labelledby="upload-bot-modal-title"
        aria-describedby="upload-bot-modal-description"
      />
    </section>
  );
};
