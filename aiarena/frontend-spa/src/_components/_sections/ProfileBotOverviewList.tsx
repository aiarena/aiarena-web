import React, { useState } from "react";

import { graphql, useFragment } from "react-relay";
import { ProfileBotOverviewList_viewer$key } from "./__generated__/ProfileBotOverviewList_viewer.graphql";
import { getNodes } from "@/_lib/relayHelpers";
import MainButton from "../_props/MainButton";
import UploadBotModal from "./_modals/UploadBotModal";
import ProfileBot from "./ProfileBot";
import { ProfileBotOverviewList_user$key } from "./__generated__/ProfileBotOverviewList_user.graphql";

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

  return (
    <div className="bg-customBackgroundColor1">
      <div className="flex justify-between ">
        <div className="flex gap-2 pb-2 mt-auto flex-wrap">
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
        {/* <h2 className="text-2xl font-bold text-customGreen mb-4">Your Bots</h2> */}
        <div className="pb-4">
          <div className="hidden md:block">
            <MainButton
              onClick={() => setUploadBotModalOpen(true)}
              text="Upload Bot"
            />
          </div>
          <div className="block md:hidden">
            <MainButton onClick={() => setUploadBotModalOpen(true)} text="+" />
          </div>
        </div>
      </div>

      <ul className="space-y-12">
        {getNodes(userData?.ownBots).map((bot) => (
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
