import React from "react";
import BotHeaderSection from "./_profile/BotHeaderSection";
import BotCompetitionsSection from "./_profile/BotCompetitionSection";
import { Bot } from "./ProfileBotOverviewList";

export interface ProfileBotProps {
  bot: Bot;
}

export default function ProfileBot({bot} : ProfileBotProps) {
  return (
    <div className="rounded-lg bg-gray-800 text-white shadow-md shadow-black">
      {/* Header Section */}
      <BotHeaderSection bot={bot} />

      {/* Active Competitions Section */}
      <BotCompetitionsSection bot={bot} />
    </div>
  );
}
