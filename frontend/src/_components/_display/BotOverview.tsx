import { getPublicPrefix } from "@/_lib/getPublicPrefix";
import Image from "next/image";
import React from "react";

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


interface Bot {
  id: string;
  name: string;
  race: string;
  created: string;
  lastUpdated: string;
  trophies?: Trophy[]
  activeCompetitions: ActiveCompetition[];
}

const BotOverview: React.FC = () => {
  const bots: Bot[] = [
    {
        id: "bot-1",
        name: "AlphaBot",
        race: "Zerg",
        created: "09. Sept. 2024 - 16:17:37",
        lastUpdated: "10. Sept. 2024 - 02:34:06",
        trophies: [
            { title: "SC2 AI Arena Season 1 - Top 10", image: "elite.webp" },
            { title: "1st Place - SC2 AI Arena Season 2", image: "titan.webp" },
            { title: "3rd Place - SC2 AI Arena Season 3", image: "optimizer.webp" },
            { title: "1st Place - ESChamp ProBots 2021 Season 2", image: "elite.webp" },
            { title: "1st Place - ESChamp ProBots 2022 Season 1", image: "elite.webp" },
          ],
        activeCompetitions: [
          {
            name: "Positive_Null - Sc2 AI Arena 2024 Pre-Season 3",
            currentELO: 1484,
            highestELO: 1595,
            matches: 1850,
            winRate: "51.57%",
            lossRate: "35.03%",
            crashes: "0.86%",
            rank: "titan",
          },
          {
            name: "Winter Championship 2024",
            currentELO: 1502,
            highestELO: 1600,
            matches: 1900,
            winRate: "52.10%",
            lossRate: "34.50%",
            crashes: "1.20%",
            rank: "elite",
          },
        ],
      },
      {
        id: "bot-2",
        name: "BetaBot",
        race: "Protoss",
        created: "05. Oct. 2024 - 11:14:22",
        lastUpdated: "06. Oct. 2024 - 09:20:15",
        activeCompetitions: [
                ],
      },
      {
        id: "bot-3",
        name: "GammaBot",
        race: "Terran",
        created: "15. Aug. 2024 - 13:42:11",
        lastUpdated: "18. Aug. 2024 - 22:58:00",
        activeCompetitions: [
          {
            name: "Meteor Clash 2024",
            currentELO: 1703,
            highestELO: 1758,
            matches: 2300,
            winRate: "59.10%",
            lossRate: "28.90%",
            crashes: "1.00%",
            rank: "optimizer",
          },
         
        ],
      },
      {
        id: "bot-4",
        name: "DeltaBot",
        race: "Zerg",
        created: "20. Nov. 2024 - 09:35:50",
        lastUpdated: "22. Nov. 2024 - 18:40:33",
        activeCompetitions: [
          {
            name: "Omega Cup 2024",
            currentELO: 1205,
            highestELO: 1285,
            matches: 870,
            winRate: "41.10%",
            lossRate: "45.90%",
            crashes: "5.00%",
            rank: "titan",
          },
          {
            name: "Nebula Championship 2024",
            currentELO: 1320,
            highestELO: 1380,
            matches: 1450,
            winRate: "49.30%",
            lossRate: "39.70%",
            crashes: "3.00%",
            rank: "elite",
          },
          {
            name: "Aurora Open 2024",
            currentELO: 1810,
            highestELO: 1850,
            matches: 2600,
            winRate: "61.50%",
            lossRate: "25.30%",
            crashes: "0.50%",
            rank: "optimizer",
          },
          {
            name: "Photon Clash Season 3",
            currentELO: 1720,
            highestELO: 1790,
            matches: 2200,
            winRate: "57.40%",
            lossRate: "30.10%",
            crashes: "2.50%",
            rank: "elite",
          },
        ],
      },
    
  ];
  return (
    <div className="bg-customBackgroundColor1 p-6 border border-gray-700">
      <div className="flex justify-between">
        <button className="bg-customGreen">Sort Filter select open button</button>
        <h2 className="text-2xl font-bold text-customGreen mb-4">Your Bots</h2>
        <div>
          <input /> <button>Search!</button>
        </div>
      </div>
      <div className="space-y-12">
        {bots.map((bot) => (
          <div
            key={bot.id}
            className="border rounded-lg bg-gray-800 text-white shadow-md border-indigo-500"
          >
            {/* Header */}
            <div className="p-4 border-b border-gray-600 bg-gray-900 flex items-center justify-between rounded-t-lg">
              {/* Left Section (Name and Race) */}
              <div className="flex flex-col">
                <h3 className="font-bold text-lg text-customGreen">{bot.name}</h3>
                <p className="text-sm text-gray-400">
                  <span className="font-bold">Race:</span> {bot.race}
                </p>
              </div>

              {/* Middle Section (Update Dates) */}
              <div className="text-sm text-gray-400 text-center">
                <p>
                  <span className="font-bold">Created:</span> {bot.created}
                </p>
                <p>
                  <span className="font-bold">Last Updated:</span> {bot.lastUpdated}
                </p>
              </div>

              {/* Right Section (Edit Button) */}
              <button className="text-sm text-white bg-indigo-500 px-3 py-1 rounded-md hover:bg-indigo-400 transition">
                Edit Bot
              </button>
            </div>

            {/* Trophies Section */}
            {bot.trophies && bot.trophies.length > 0 ? (
              <div className="p-4 border-b border-gray-600 bg-gray-700">
                <h4 className="text-lg font-bold text-customGreen mb-2">Trophies</h4>
                <div className="overflow-x-auto whitespace-nowrap space-x-4 flex">
                  {bot.trophies.map((trophy, index) => (
                    <div
                      key={index}
                      className="flex-shrink-0 flex items-center bg-gray-800 p-3 border border-gray-600 rounded-md"
                    >
                      <div className="w-12 h-12 relative mr-2">
                        <Image
                          src={`${getPublicPrefix()}/demo_assets/${trophy.image}`}
                          alt={trophy.title}
                          layout="fill"
                          objectFit="contain"
                        />
                      </div>
                      <p className="text-xs text-gray-300">{trophy.title}</p>
                    </div>
                  ))}
                </div>
              </div>
            ) : (
              <div className="p-4 border-b border-gray-600 bg-gray-700">
                <h4 className="text-lg font-bold text-customGreen mb-2">Trophies</h4>
                <p className="text-sm text-gray-400">This bot has no trophies yet.</p>
              </div>
            )}

            {/* Active Competitions */}
            <div className="p-4">
              <h4 className="text-sm font-semibold text-gray-300 mb-2">
                Active Competitions:
              </h4>
              <div className="space-y-4">
                {bot.activeCompetitions.map((comp, index) => (
                  <div
                    key={index}
                    className="grid grid-cols-1 md:grid-cols-2 gap-4 items-start bg-gray-700 p-4 border border-gray-600 rounded-lg hover:bg-gray-600 transition cursor-pointer"
                  >
                    {/* Competition Info */}
                    <div>
                      <p className="text-sm font-semibold text-indigo-400 mb-1">
                        {comp.name}
                      </p>
                      <ul className="text-xs text-gray-300">
                        <li>
                          <span className="font-bold">Matches:</span> {comp.matches}
                        </li>
                        <li>
                          <span className="font-bold">Win/Loss:</span>{" "}
                          <span className="text-customGreen">{comp.winRate}</span> /{" "}
                          {comp.lossRate}
                        </li>
                        <li>
                          <span className="font-bold">Crashes:</span>{" "}
                          <span className="text-red-500">{comp.crashes}</span>
                        </li>
                      </ul>
                    </div>

                    {/* ELO Details */}
                    <div className="flex flex-col">
                      <span className="text-xs font-bold">
                        Current ELO: {comp.currentELO}
                      </span>
                      <span className="text-xs font-bold">
                        Highest ELO: {comp.highestELO}
                      </span>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};

export default BotOverview;