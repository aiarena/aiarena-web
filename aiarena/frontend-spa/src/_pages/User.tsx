import { Suspense } from "react";
import { graphql, useLazyLoadQuery } from "react-relay";
import { ProfileQuery } from "./__generated__/ProfileQuery.graphql";

import SettingsProfileSection from "@/_components/_profile/SettingsProfileSection";
import LoadingSpinnerGray from "@/_components/_display/LoadingSpinnerGray";

export default function User() {
  const data = useLazyLoadQuery<ProfileQuery>(
    graphql`
      query ProfileQuery {
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
      <div className=" flex justify-center text-gray-300">
        <div className="max-w-7xl w-full">
          {/* Content Sections */}
          <div className="mt-8">
            <div id="settigns">
              <Suspense fallback={<LoadingSpinnerGray />}>
                <SettingsProfileSection viewer={data.viewer} />
              </Suspense>
            </div>
          </div>
        </div>
      </div>
    </>
  );
}
