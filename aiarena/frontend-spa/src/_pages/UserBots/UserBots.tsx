import { Suspense } from "react";
import { graphql, useLazyLoadQuery } from "react-relay";

import LoadingSpinner from "@/_components/_display/LoadingSpinnerGray";
import { UserBotsQuery } from "./__generated__/UserBotsQuery.graphql";
import { UserBotsSection } from "./UserBotsSection";

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
      <Suspense fallback={<LoadingSpinner color="light-gray" />}>
        <UserBotsSection viewer={data.viewer} />
      </Suspense>
    </>
  );
}
