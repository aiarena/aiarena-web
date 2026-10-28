import { getPublicPrefix } from "@/_lib/getPublicPrefix";
import { graphql, useFragment } from "react-relay";
import clsx from "clsx";
import { PatreonIcon_user$key } from "./__generated__/PatreonIcon_user.graphql";

interface PatreonIconProps {
  user: PatreonIcon_user$key;
}

export default function PatreonIcon(props: PatreonIconProps) {
  const user = useFragment(
    graphql`
      fragment PatreonIcon_user on UserType {
        patreonLevel
      }
    `,
    props.user,
  );
  if (
    user.patreonLevel === "NONE" ||
    user.patreonLevel === null ||
    user.patreonLevel === undefined
  ) {
    return null;
  } else {
    return (
      <img
        src={`${getPublicPrefix()}/bot-icons/${user.patreonLevel.toLowerCase()}.png`}
        alt={`${user.patreonLevel.toLowerCase()} icon`}
        width={22}
        height={22}
        className={clsx("mr-2")}
      />
    );
  }
}
