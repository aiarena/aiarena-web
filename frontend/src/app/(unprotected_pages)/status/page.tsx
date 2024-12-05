"use client";
import EthernetStatusDots from "@/_components/_display/EthernetStatusEffect";
import { ImageOverlayWrapper } from "@/_components/_display/ImageOverlayWrapper";
import WrappedTitle from "@/_components/_display/WrappedTitle";
import Image from "next/image";
import React from "react";

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
    <div className="bg-gray-900 p-4 rounded-md">
      <WrappedTitle title="Activity Feed" />
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

const UptimeGraph = ({ title }: { title: string }) => {
  return (
    <div className="bg-gray-900 p-4 rounded-md">
      <WrappedTitle title={title} />
      <div className="h-40 bg-gray-700 flex items-center justify-center text-gray-300 mb-2">
        [Graph Placeholder]
      </div>
      <EthernetStatusDots />
    </div>
  );
};

const Stats = () => {
  return (
    <div className="bg-gray-900 p-4 rounded-md">
      <WrappedTitle title="Stats" />
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
    <div className="bg-gray-900 mt-8 mb-8 p-4 rounded-md">
      <WrappedTitle title="Thank you" />
      Thank you Spacemen for supporting AI arena!
      <p>Heart icon</p>
    </div>
  );
};

const HomePage = () => {
  return (
    <div className="bg-gray-800 min-h-screen p-8">
      <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
        <div className="col-span-1 md:col-span-2">
          <ActivityFeed />
        </div>
        <div>
          <Stats />
          <Thanks />
        </div>
      </div>

      <div className="mt-8 grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
        <UptimeGraph title="Streaming Server 1 Uptime" />
        <UptimeGraph title="Streaming Server 2 Uptime" />
        <UptimeGraph title="Website Uptime" />
        <UptimeGraph title="Simulation Server 1 Uptime" />
        <UptimeGraph title="Simulation Server 2 Uptime" />
        <UptimeGraph title="Simulation Server 3 Uptime" />
      </div>
    </div>
  );
};

export default HomePage;
