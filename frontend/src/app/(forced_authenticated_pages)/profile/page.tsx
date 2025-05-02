"use client";
import { useEffect, useState } from "react";
import TabNavigation from "@/_components/_nav/TabNav";
import PreFooterSpacer from "@/_components/_display/PreFooterSpacer";
import SettingsProfileSection from "@/_components/_display/_profile/SettingsProfileSection";
import RequestMatchSection from "@/_components/_display/_profile/RequestMatchSection";
import { redirect } from "next/navigation";
import { ProfileBotOverviewList } from "@/_components/_display/ProfileBotOverviewList";
import {
  graphql,
  PreloadedQuery,
  usePreloadedQuery,
  useQueryLoader,
} from "react-relay";
import { pageProfileDashboardQuery } from "./__generated__/pageProfileDashboardQuery.graphql";
import { getPublicPrefix } from "@/_lib/getPublicPrefix";
import { PlaceholderLoadingFallback } from "@/_components/_display/PlaceholderLoadingFallback";

// This is a working example of a client render page

const ProfileQuery = graphql`
  query pageProfileDashboardQuery {
    viewer {
      ...ProfileBotOverviewList_viewer
      ...RequestMatchSection_viewer
      ...SettingsProfileSection_viewer
    }
  }
`;

export default function Page() {
  const [queryRef, loadQuery] =
    useQueryLoader<pageProfileDashboardQuery>(ProfileQuery);

  useEffect(() => {
    loadQuery({});
  }, [loadQuery]);

  return (
    <div className="container mx-auto p-4">
      <h1 className="text-2xl font-bold mb-4">Profile</h1>
      {!queryRef ? (
        <PlaceholderLoadingFallback />
      ) : (
        <ProfileContentRender queryRef={queryRef} />
      )}
    </div>
  );
}

type ProfileContentProps = {
  queryRef: PreloadedQuery<pageProfileDashboardQuery>;
};

function ProfileContentRender({ queryRef }: ProfileContentProps) {
  const data = usePreloadedQuery<pageProfileDashboardQuery>(
    ProfileQuery,
    queryRef
  );
  const [activeTab, setActiveTab] = useState("Bots");
  useEffect(() => {
    if (!data.viewer) {
      redirect(`${getPublicPrefix()}/`);
    }
  }, [data]);
  return (
    <>
      <div className="min-h-screen flex justify-center text-gray-300">
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
            {data.viewer ? (
              <>
                {activeTab === "Bots" && (
                  <div id="bot-overview">
                    <ProfileBotOverviewList viewer={data.viewer} />
                  </div>
                )}

                {activeTab === "Requested Matches" && (
                  <div id="matches">
                    <RequestMatchSection viewer={data.viewer} />
                  </div>
                )}

                {data && activeTab === "Settings" && (
                  <div id="settigns">
                    <SettingsProfileSection viewer={data.viewer} />
                  </div>
                )}
              </>
            ) : null}
          </div>
        </div>
      </div>
      <PreFooterSpacer />
    </>
  );
}
