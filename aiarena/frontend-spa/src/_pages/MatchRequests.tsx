import { Suspense } from "react";
import { graphql, useLazyLoadQuery } from "react-relay";
import { ProfileQuery } from "./__generated__/ProfileQuery.graphql";
import RequestMatchSection from "@/_components/_profile/RequestMatchSection";

import LoadingSpinnerGray from "@/_components/_display/LoadingSpinnerGray";

export default function MatchRequests() {
  const data = useLazyLoadQuery<ProfileQuery>(
    graphql`
      query ProfileQuery {
        viewer {
          ...RequestMatchSection_viewer
        }
      }
    `,
    {}
  );

  if (!data.viewer) {
    return (
      <>
        <p>No viewer</p>
      </>
    );
  }

  return (
    <>
      <Suspense fallback={<LoadingSpinnerGray />}>
        <RequestMatchSection viewer={data.viewer} />
      </Suspense>
    </>
  );
}
