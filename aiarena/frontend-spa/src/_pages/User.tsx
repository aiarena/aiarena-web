import { Suspense } from "react";
import { graphql, useLazyLoadQuery } from "react-relay";
import { ProfileQuery } from "./__generated__/ProfileQuery.graphql";

import SettingsProfileSection from "@/_components/_sections/SettingsProfileSection";
import LoadingSpinnerGray from "@/_components/_display/LoadingSpinnerGray";

export default function User() {
  const data = useLazyLoadQuery<ProfileQuery>(
    graphql`
      query UserQuery {
        viewer {
          ...SettingsProfileSection_viewer
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
        <SettingsProfileSection viewer={data.viewer} />
      </Suspense>
    </>
  );
}
