import React, { useState } from "react";
import MainButton from "../_props/MainButton";
import ProfileBot from "./ProfileBot";
import UploadBotModal from "./_profile/UploadBotModal";
import { graphql, useFragment } from "react-relay";
import { ProfileBotOverviewList_viewer$key } from "./__generated__/ProfileBotOverviewList_viewer.graphql";
import { getNodes } from "@/_lib/relayHelpers";

interface ProfileBotOverviewListProps {
  viewer: ProfileBotOverviewList_viewer$key;
}

export const ProfileBotOverviewList: React.FC<ProfileBotOverviewListProps> = (
  props,
) => {
  const viewer = useFragment(
    graphql`
      fragment ProfileBotOverviewList_viewer on ViewerType {
        activeBotsLimit
        user {
          ownBots {
            edges {
              node {
                id
                ...ProfileBot_bot
              }
            }
          }
        }
      }
    `,
    props.viewer,
  );

  const [isUploadBotModalOpen, setUploadBotModalOpen] = useState(false);

  return (
    <div className="bg-customBackgroundColor1 p-4 border border-gray-700">
      <div className="flex justify-between ">
        <div className="flex gap-2 pb-2 mt-auto flex-wrap">
          {viewer.activeBotsLimit ? (
            <span className="flex word-wrap">
              X / {viewer.activeBotsLimit} active competition participations.
            </span>
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
        {getNodes(viewer.user?.ownBots).map((bot) => (
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
