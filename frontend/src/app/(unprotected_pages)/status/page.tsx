"use client";
import EthernetStatusDots from "@/_components/_display/EthernetStatusEffect";
import { ImageOverlayWrapper } from "@/_components/_display/ImageOverlayWrapper";
import TitleWrapper from "@/_components/_display/TitleWrapper";
import Image from "next/image";
import React from "react";
import mockUptimeData from "@/_data/mockUptime.json";
import PreFooterSpacer from "@/_components/_display/PreFooterSpacer";
import { notFound } from "next/navigation"; // Import the notFound function
import { getFeatureFlags }from "@/_data/featureFlags"

const ActivityFeed = () => {
  const activities = [
    { time: "1h ago", event: "Bot Arty was updated." },
    { time: "4h ago", event: "Bot BenBotBC was updated." },
    { time: "7h ago", event: "Bot TerrAIn-Python was updated." },
    { time: "7h ago", event: "Bot DominionDog was updated." },
    { time: "9h ago", event: "Bot Roro was updated." },
    { time: "9h ago", event: "Bot Zozo was updated." },
    { time: "9h ago", event: "Bot Dodo was updated." },
    { time: "15h ago", event: "Bot Clicadinha was updated." },
    { time: "1d ago", event: "Bot DemonZ was updated." },
    { time: "1d, 6h ago", event: "Bot PerilousProtossBot was updated." },
    { time: "1d, 6h ago", event: "Bot Akamight was updated." },
    { time: "1d, 19h ago", event: "Bot Eris was updated." },
    { time: "2d, 17h ago", event: "Bot ThomTest was updated." },
    { time: "2d, 19h ago", event: "Bot nida was updated." },
    { time: "3d ago", event: "Bot SharkbotTest was updated." },
  ];

  return (
    <div className="bg-customBackgroundColor1 p-4 rounded-md shadow shadow-black ">
      <TitleWrapper title="Activity Feed" />
      <ul className="space-y-2">
        {activities.map((activity, index) => (
          <li key={index} className="text-gray-300">
            <span className="font-semibold text-customGreen">
              {activity.time}
            </span>{" "}
            – {activity.event}
          </li>
        ))}
      </ul>
    </div>
  );
};

const UptimeGraph = ({
  title,
  data,
}: {
  title: string;
  data: { hour: string; uptime: number }[];
}) => {
  return (
    <div className="shadow shadow-black bg-customBackgroundColor1 p-4 rounded-md">
      <TitleWrapper title={title} />
      <div className="h-40 bg-customBackgroundColor1D1  flex items-end justify-between text-gray-300 mb-2 p-2">
        {data.map((entry, index) => (
          <div
            key={index}
            className="w-2 bg-customGreen brightness-75"
            style={{
              height: `${entry.uptime}%`,
              transition: "height 0.3s ease",
            }}
            title={`Hour ${entry.hour}: ${entry.uptime}% uptime`}
          ></div>
        ))}
      </div>
      <EthernetStatusDots />
    </div>
  );
};
const Stats = () => {
  return (
    <div className="bg-customBackgroundColor1 p-4 rounded-md shadow shadow-black ">
      <TitleWrapper title="Stats" />
      <ul className="space-y-2 text-gray-300">
        <li>
          Date:{" "}
          <span className="font-semibold text-customGreen">17. Oct. 2024</span>
        </li>
        <li>
          Time:{" "}
          <span className="font-semibold text-customGreen">05:00:59 UTC</span>
        </li>
        <li>
          Matches (1h):{" "}
          <span className="font-semibold text-customGreen">105</span>
        </li>
        <li>
          Matches (24h):{" "}
          <span className="font-semibold text-customGreen">2560</span>
        </li>
        <li>
          Arena Clients:{" "}
          <span className="font-semibold text-customGreen">22</span>
        </li>
        <li>
          Build: <span className="font-semibold text-customGreen">494</span>
        </li>
      </ul>
    </div>
  );
};

const Thanks = () => {
  return (
    <div className="bg-customBackgroundColor1 mt-8 mb-8 p-4 rounded-md shadow shadow-black ">
      <TitleWrapper title="Thank you" />
      Thank you Spacemen for supporting AI arena!
      <p>Heart icon</p>
    </div>
  );
};

const HomePage = () => {
  const  statusPage = getFeatureFlags().statusPage 
  const  serverStatus = getFeatureFlags().statusServerStatus
  const  supporters = getFeatureFlags().supporters


  if (!statusPage) {
    notFound()
    return null
  }

  const uptimeData = mockUptimeData;
  return (
    <>
      <div className=" min-h-screen max-w-7xl m-auto pt-8">
        <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
          <div className="col-span-1 md:col-span-2">
            <ActivityFeed />
          </div>
          <div>
            <Stats />
            {supporters?
            <Thanks /> : null}

          </div>
        </div>
        {

          serverStatus ? 
        <div className="mt-8 grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
          {uptimeData.map((server) => (
            <UptimeGraph
              key={server.serverName}
              title={server.serverName}
              data={server.data}
            />
          ))}
        </div>
        : null
        }
      </div>
      <PreFooterSpacer />
    </>
  );
};

export default HomePage;
