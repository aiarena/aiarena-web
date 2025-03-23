"use client";
import { useState } from "react";
import TabNavigation from "@/_components/_nav/TabNav";
import PreFooterSpacer from "@/_components/_display/PreFooterSpacer";
import SettingsProfileSection from "@/_components/_display/_profile/SettingsProfileSection";
import RequestMatchSection from "@/_components/_display/_profile/RequestMatchSection";
import { redirect } from "next/navigation";
import { ProfileBotOverviewList } from "@/_components/_display/ProfileBotOverviewList";
import { graphql, useLazyLoadQuery } from "react-relay";
import { pageProfileDashboardQuery } from "./__generated__/pageProfileDashboardQuery.graphql";

export default function Page() {
  const data = useLazyLoadQuery<pageProfileDashboardQuery>(
    graphql`
      query pageProfileDashboardQuery {
        viewer {
          user {
            id
            username
            patreonLevel
            dateJoined
            avatarUrl
          }
          apiToken
          email
          activeBotsLimit
          requestMatchesLimit
          requestMatchesCountLeft
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
    redirect("/");
  }

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
          </div>
        </div>
      </div>
      <PreFooterSpacer />
    </>
  );
}
