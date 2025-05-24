import { graphql, useFragment } from "react-relay";

import UserBotCompetition from "./UserBotCompetitions";
import UserBotHeader from "./UserBotHeader";
import { UserBot_bot$key } from "./__generated__/UserBot_bot.graphql";

export interface UserBotProps {
  bot: UserBot_bot$key;
}

export default function UserBot(props: UserBotProps) {
  const bot = useFragment(
    graphql`
      fragment UserBot_bot on BotType {
        id
        name
        ...UserBotHeader_bot
        ...UserBotCompetitions_bot
      }
    `,
    props.bot
  );
  return (
    <div className="rounded-lg text-white  border border-neutral-600 shadow-lg shadow-black">
      {/* Header Section */}
      <UserBotHeader bot={bot} />

      {/* Active Competitions Section */}
      <UserBotCompetition bot={bot} />
    </div>
  );
}
