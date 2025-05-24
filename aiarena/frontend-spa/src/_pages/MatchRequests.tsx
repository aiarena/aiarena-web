import { Suspense } from "react";
import { graphql, useLazyLoadQuery } from "react-relay";
import { ProfileQuery } from "./__generated__/ProfileQuery.graphql";
import RequestMatchSection from "@/_components/_sections/RequestMatchSection";

import LoadingSpinner from "@/_components/_display/LoadingSpinnerGray";

export default function MatchRequests() {
  const data = useLazyLoadQuery<ProfileQuery>(
    graphql`
      query MatchRequestsQuery {
        viewer {
          ...RequestMatchSection_viewer
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
