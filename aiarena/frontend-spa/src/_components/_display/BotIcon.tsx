import { getPublicPrefix } from "@/_lib/getPublicPrefix";
import { graphql, useFragment } from "react-relay";
import { BotIcon_user$key } from "./__generated__/BotIcon_user.graphql";

interface BotIconProps {
  user: BotIcon_user$key;
}

export default function BotIcon(props: BotIconProps) {
  const user = useFragment(
    graphql`
      fragment BotIcon_user on UserType {
        patreonLevel
      }
    `,
    props.user
  );
  if (
    user.patreonLevel === "NONE" ||
    user.patreonLevel === null ||
    user.patreonLevel === undefined
  ) {
    return null;
  } else {
    return (
      <div>
        <img
          src={`${getPublicPrefix()}/bot-icons/${user.patreonLevel.toLowerCase()}.png`}
          alt={`${user.patreonLevel.toLowerCase()} icon`}
          width={30}
          height={30}
        />
      </div>
    );
  }
}
