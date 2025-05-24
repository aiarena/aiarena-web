import { Suspense } from "react";
import { graphql, useLazyLoadQuery } from "react-relay";

import RequestMatchSection from "@/_components/_sections/UserMatchRequestsSection";

import LoadingSpinner from "@/_components/_display/LoadingSpinnerGray";
import { UserMatchRequestsQuery } from "./__generated__/UserMatchRequestsQuery.graphql";

export default function UserMatchRequests() {
  const data = useLazyLoadQuery<UserMatchRequestsQuery>(
    graphql`
      query UserMatchRequestsQuery {
        viewer {
          ...UserMatchRequestsSection_viewer
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
        <RequestMatchSection viewer={data.viewer} />
      </Suspense>
    </>
  );
}
