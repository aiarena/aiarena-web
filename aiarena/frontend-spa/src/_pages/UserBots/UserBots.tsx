import { Suspense } from "react";
import { graphql, useLazyLoadQuery } from "react-relay";

import { UserBotsQuery } from "./__generated__/UserBotsQuery.graphql";
import { UserBotsSection } from "./UserBotsSection";
import DisplaySkeletonUserBots from "@/_components/_display/_skeletons/DisplaySkeletonUserBots";

export default function UserBots() {
  const data = useLazyLoadQuery<UserBotsQuery>(
    graphql`
      query UserBotsQuery {
        viewer {
          ...UserBotsSection_viewer
        }
      }
    `,
    {},
  );

  if (!data.viewer) {
    window.location.replace("/accounts/login");
    return null;
  }

  return (
    <>
      <Suspense fallback={<DisplaySkeletonUserBots />}>
        <UserBotsSection viewer={data.viewer} />
      </Suspense>
    </>
  );
}
