import React from "react";
import BotHeaderSection from "./_profile/BotHeaderSection";
import BotCompetitionsSection from "./_profile/BotCompetitionSection";
// import { Bot } from "./ProfileBotOverviewList";
import { graphql, useFragment } from "react-relay";
import {
  ProfileBot_bot$data,
  ProfileBot_bot$key,
} from "./__generated__/ProfileBot_bot.graphql";

export interface ProfileBotProps {
  bot: ProfileBot_bot$key;
}

export default function ProfileBot(props: ProfileBotProps) {
  const bot = useFragment(
    graphql`
      fragment ProfileBot_bot on BotType {
        id
        name
        ...BotHeaderSection_bot
        ...BotCompetitionSection_bot
      }
    `,
    props.bot,
  );
  return (
    <div className="rounded-lg bg-gray-800 text-white shadow-md shadow-black">
      {/* Header Section */}
      <BotHeaderSection bot={bot} />

      {/* Active Competitions Section */}
      <BotCompetitionsSection bot={bot} />
    </div>
  );
}
