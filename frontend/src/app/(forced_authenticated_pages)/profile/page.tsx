"use client";
import { useViewerContext } from "@/_components/providers/ViewerProvider";
import { useSignOut } from "@/_components/_hooks/useSignOut";
import { useRouter } from "next/navigation";
import { useState } from "react";
import TabNavigation from "@/_components/_nav/TabNav";
import ProfileBotOverviewList from "@/_components/_display/ProfileBotOverviewList";
import PreFooterSpacer from "@/_components/_display/PreFooterSpacer";
import SettingsProfileSection from "@/_components/_display/_profile/SettingsProfileSection";
import RequestMatchesSection from "@/_components/_display/_profile/RequestMatchSection";
import { useUserBots } from "@/_components/_hooks/useUserBot";
import { useViewer } from "@/_components/_hooks/useViewer";
import { redirect } from 'next/navigation';


export default function Page() {
  const [signOut] = useSignOut();
  const router = useRouter();
  const viewer  = useViewer();

  const [activeTab, setActiveTab] = useState("Bots");
  const userBots = useUserBots(viewer?.user?.id  || null);
  if (viewer?.user === null ) {
    // console.log("Compared")
    // router.push("/");
    redirect('/');    // return null;
  }
  



  return (
    <>
      <div className="min-h-screen flex justify-center">
        <div className="mx-auto py-8 px-4 max-w-7xl bg-gray-800 w-full">
          {/* Navigation Tabs */}
          <TabNavigation
            tabs={[
              { name: "Bots", href: "#bot-overview" },
              // { name: "Achievements", href: "#achievements" },
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
                  <ProfileBotOverviewList bots={userBots} activeBotsLimit = {viewer?.user.activeBotsLimit} />
              </div>
            )}

            {activeTab === "Requested Matches" && (
              <div id="matches">
                  <RequestMatchesSection
                  requestMatchesCountLeft={viewer?.user?.requestMatchesCountLeft}
                  requestMatchesLimit={viewer?.user?.requestMatchesLimit}
                />
              </div>
            )}

            {viewer && activeTab === "Settings" && (
              <div id="settigns">
              
                <SettingsProfileSection viewer={viewer || null} />
            
                </div>
            )}
          </div>
        </div>
      </div>
      <PreFooterSpacer />
    </>
  );
}
