import { getPublicPrefix } from "@/_lib/getPublicPrefix";
import Image from "next/image";
import React, { useState } from "react";
import MainButton from "../_props/MainButton";
import ProfileBot from "./ProfileBot";
import UploadBotModal from "./_profile/UploadBotModal";

interface ActiveCompetition {
  name: string;
  currentELO: number;
  highestELO: number;
  matches: number;
  winRate: string;
  lossRate: string;
  crashes: string;
  rank: string;
}

interface Trophy {
  title: string;
  image: string;
}

export interface Bot {
  id: string;
  name: string;
  created?: string;
  type? : string;
  url? : string;
  botData?: string;
  botDataEnabled?: boolean;
  botDataPubliclyDownloadable?: boolean;
  botZip?: string;
  botZipPubliclyDownloadable?: boolean;

  botZipUpdated?: string;

  wikiArticle?: string;
  trophies?: Trophy[];
  activeCompetitions?: ActiveCompetition[];
}

interface ProfileBotOverviewListProps {
  bots: Bot[];
  activeBotsLimit?: number;
}

const ProfileBotOverviewList: React.FC<ProfileBotOverviewListProps> = ({
  bots,
  activeBotsLimit,
}) => {
  const [isUploadBotModalOpen, setUploadBotModalOpen] = useState(false);

  return (
    <div className="bg-customBackgroundColor1 p-4 border border-gray-700">
      <div className="flex justify-between ">
        <div className="flex gap-2 pb-2 mt-auto flex-wrap">
          {activeBotsLimit ? (
            <span className="flex word-wrap">
              You may have {activeBotsLimit} active competition participations.
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
        {bots.map((bot, id) => (
          <li key={id}>
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

export default ProfileBotOverviewList;
