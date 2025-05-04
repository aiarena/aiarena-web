// "use client";
import TabNavigation from "@/_components/_nav/TabNav";
import { Suspense, useState } from "react";
import { graphql, useLazyLoadQuery } from "react-relay";
import { ProfileQuery } from "./__generated__/ProfileQuery.graphql";
import { ProfileBotOverviewList } from "@/_components/_profile/ProfileBotOverviewList";
import RequestMatchSection from "@/_components/_profile/RequestMatchSection";
import SettingsProfileSection from "@/_components/_profile/SettingsProfileSection";
import LoadingSpinnerGray from "@/_components/_display/LoadingSpinnerGray";

export default function Profile() {
  const data = useLazyLoadQuery<ProfileQuery>(
    graphql`
      query ProfileQuery {
        viewer {
          ...ProfileBotOverviewList_viewer
          ...RequestMatchSection_viewer
          ...SettingsProfileSection_viewer
        }
      }
    `,
    {}
  );

  const [activeTab, setActiveTab] = useState("Bots");
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
        <div className="mx-auto py-8 px-4 max-w-7xl bg-gray-800 w-full">
          {/* Navigation Tabs */}
          <TabNavigation
            tabs={[
              { name: "Bots", href: "#bot-overview" },
              { name: "Requested Matches", href: "#matches" },
              { name: "Settings", href: "#settings" },
            ]}
            activeTab={activeTab}
            setActiveTab={setActiveTab}
          />

          {/* Content Sections */}
          <div className="mt-8">
            {activeTab === "Bots" && (
              <div id="bot-overview">
                <Suspense fallback={<LoadingSpinnerGray />}>
                  <ProfileBotOverviewList viewer={data.viewer} />
                </Suspense>
              </div>
            )}

            {activeTab === "Requested Matches" && (
              <div id="matches">
                <Suspense fallback={<LoadingSpinnerGray />}>
                  <RequestMatchSection viewer={data.viewer} />
                </Suspense>
              </div>
            )}

            {data && activeTab === "Settings" && (
              <div id="settigns">
                <Suspense fallback={<LoadingSpinnerGray />}>
                  <SettingsProfileSection viewer={data.viewer} />
                </Suspense>
              </div>
            )}
          </div>
        </div>
      </div>
    </>
  );
}
