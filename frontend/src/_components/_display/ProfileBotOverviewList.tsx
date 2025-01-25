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
  race?: string;
  botZipUpdated?: string;
  biography?: string;
  // isZipPublic?: boolean;
  botDataPubliclyDownloadable?: boolean;
  botDataEnabled?: boolean;
  trophies?: Trophy[];
  activeCompetitions?: ActiveCompetition[];
}

// const bots: Bot[] = [
//   {
//     id: "bot-1",
//     name: "AlphaBot",
//     race: "Zerg",
//     created: "09. Sept. 2024 - 16:17:37",
//     lastUpdated: "10. Sept. 2024 - 02:34:06",
//     trophies: [
//       { title: "SC2 AI Arena Season 1 - Top 10", image: "elite.webp" },
//       { title: "1st Place - SC2 AI Arena Season 2", image: "titan.webp" },
//       { title: "3rd Place - SC2 AI Arena Season 3", image: "optimizer.webp" },
//       {
//         title: "1st Place - ESChamp ProBots 2021 Season 2",
//         image: "elite.webp",
//       },
//       {
//         title: "1st Place - ESChamp ProBots 2022 Season 1",
//         image: "elite.webp",
//       },
//     ],
//     activeCompetitions: [
//       {
//         name: "Positive_Null - Sc2 AI Arena 2024 Pre-Season 3",
//         currentELO: 1484,
//         highestELO: 1595,
//         matches: 1850,
//         winRate: "51.57%",
//         lossRate: "35.03%",
//         crashes: "0.86%",
//         rank: "titan",
//       },
//       {
//         name: "Winter Championship 2024",
//         currentELO: 1502,
//         highestELO: 1600,
//         matches: 1900,
//         winRate: "52.10%",
//         lossRate: "34.50%",
//         crashes: "1.20%",
//         rank: "elite",
//       },
//     ],
//   },
//   {
//     id: "bot-2",
//     name: "BetaBot",
//     race: "Protoss",
//     created: "05. Oct. 2024 - 11:14:22",
//     lastUpdated: "06. Oct. 2024 - 09:20:15",
//     activeCompetitions: [],
//   },
//   {
//     id: "bot-3",
//     name: "GammaBot",
//     race: "Terran",
//     created: "15. Aug. 2024 - 13:42:11",
//     lastUpdated: "18. Aug. 2024 - 22:58:00",
//     activeCompetitions: [
//       {
//         name: "Meteor Clash 2024",
//         currentELO: 1703,
//         highestELO: 1758,
//         matches: 2300,
//         winRate: "59.10%",
//         lossRate: "28.90%",
//         crashes: "1.00%",
//         rank: "optimizer",
//       },
//     ],
//   },
//   {
//     id: "bot-4",
//     name: "DeltaBot",
//     race: "Zerg",
//     created: "20. Nov. 2024 - 09:35:50",
//     lastUpdated: "22. Nov. 2024 - 18:40:33",
//     activeCompetitions: [
//       {
//         name: "Omega Cup 2024",
//         currentELO: 1205,
//         highestELO: 1285,
//         matches: 870,
//         winRate: "41.10%",
//         lossRate: "45.90%",
//         crashes: "5.00%",
//         rank: "titan",
//       },
//       {
//         name: "Nebula Championship 2024",
//         currentELO: 1320,
//         highestELO: 1380,
//         matches: 1450,
//         winRate: "49.30%",
//         lossRate: "39.70%",
//         crashes: "3.00%",
//         rank: "elite",
//       },
//       {
//         name: "Aurora Open 2024",
//         currentELO: 1810,
//         highestELO: 1850,
//         matches: 2600,
//         winRate: "61.50%",
//         lossRate: "25.30%",
//         crashes: "0.50%",
//         rank: "optimizer",
//       },
//       {
//         name: "Photon Clash Season 3",
//         currentELO: 1720,
//         highestELO: 1790,
//         matches: 2200,
//         winRate: "57.40%",
//         lossRate: "30.10%",
//         crashes: "2.50%",
//         rank: "elite",
//       },
//     ],
//   },
// ];

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
