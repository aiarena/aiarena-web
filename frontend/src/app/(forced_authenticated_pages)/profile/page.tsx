"use client";
import { useViewerContext } from "@/_components/providers/ViewerProvider";
import { useSignOut } from "@/_components/_hooks/useSignOut";
import { useRouter } from "next/navigation";
import { useState } from "react";
import TabNavigation from "@/_components/_nav/TabNav";
// import  from "@/_components/_display/ProfileBotOverviewList";
import PreFooterSpacer from "@/_components/_display/PreFooterSpacer";
import SettingsProfileSection from "@/_components/_display/_profile/SettingsProfileSection";
import RequestMatchesSection from "@/_components/_display/_profile/RequestMatchSection";
import { useUserBots } from "@/_components/_hooks/useUserBot";
import { useViewer } from "@/_components/_hooks/useViewer";
import { redirect } from 'next/navigation';
import { useViewerRequestedMatches } from "@/_components/_hooks/useViewerRequestedMatches";
import { ProfileBotOverviewList } from "@/_components/_display/ProfileBotOverviewList";


export default function Page() {
  const [signOut] = useSignOut();
  const router = useRouter();
  const viewer  = useViewer();
  const requestedMatches = useViewerRequestedMatches();

  const [activeTab, setActiveTab] = useState("Bots");
  if (viewer === null ) {
    redirect('/');   
  }
  
  const userBots = useUserBots(viewer?.user?.id);
  




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
                  <ProfileBotOverviewList bots={userBots} activeBotsLimit = {viewer?.activeBotsLimit} />
              </div>
            )}

            {activeTab === "Requested Matches" && (
              <div id="matches">
                  <RequestMatchesSection
                  requestMatchesCountLeft={viewer?.requestMatchesCountLeft}
                  requestMatchesLimit={viewer?.requestMatchesLimit}
                  requestedMatches = {requestedMatches}
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
