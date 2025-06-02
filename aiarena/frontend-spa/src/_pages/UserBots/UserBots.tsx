import { Suspense } from "react";
import { graphql, useLazyLoadQuery } from "react-relay";
import { UserBotsSection } from "@/_components/_sections/UserBotsSection";

import LoadingSpinner from "@/_components/_display/LoadingSpinnerGray";
import { UserBotsQuery } from "./__generated__/UserBotsQuery.graphql";

export default function UserBots() {
  const data = useLazyLoadQuery<UserBotsQuery>(
    graphql`
      query UserBotsQuery {
        viewer {
          ...UserBotsSection_viewer
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
      <Suspense fallback={<LoadingSpinner color="light-gray" />}>
        <UserBotsSection viewer={data.viewer} />
      </Suspense>
    </>
  );
}
