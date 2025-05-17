import { Suspense } from "react";
import { graphql, useLazyLoadQuery } from "react-relay";
import { ProfileQuery } from "./__generated__/ProfileQuery.graphql";
import { ProfileBotOverviewList } from "@/_components/_sections/ProfileBotOverviewList";

import LoadingSpinnerGray from "@/_components/_display/LoadingSpinnerGray";

export default function UserBots() {
  const data = useLazyLoadQuery<ProfileQuery>(
    graphql`
      query UserBotsQuery {
        viewer {
          ...ProfileBotOverviewList_viewer
        }
      }
    `,
    {}
  );

  if (!data.viewer) {
    window.location.replace("/accounts/login");
    return null;
  }

  return (
    <>
      <Suspense fallback={<LoadingSpinnerGray />}>
        <ProfileBotOverviewList viewer={data.viewer} />
      </Suspense>
    </>
  );
}
