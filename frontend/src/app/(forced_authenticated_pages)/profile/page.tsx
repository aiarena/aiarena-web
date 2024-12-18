"use client";
import { useUserContext } from "@/_components/providers/UserProvider";
import { useSignOut } from "@/_components/_hooks/useSignOut";
import { useRouter } from "next/navigation";
import { useState } from "react";
import TabNavigation from "@/_components/_nav/TabNav";
import ProfileBotOverviewList from "@/_components/_display/ProfileBotOverviewList";
import PreFooterSpacer from "@/_components/_display/PreFooterSpacer";
import SettingsProfileSection from "@/_components/_display/_profile/SettingsProfileSection";
import RequestMatchesSection from "@/_components/_display/_profile/RequestMatchSection";

export default function Page() {
  const [signOut] = useSignOut();
  const router = useRouter();
  const { user, setUser, fetching } = useUserContext();
  const [activeTab, setActiveTab] = useState("Bots");

  if (user === null && fetching === false) {
    router.push("/");
    return null;
  }
  if (user === null) {
    return;
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
                <ProfileBotOverviewList />
              </div>
            )}

            {activeTab === "Requested Matches" && (
              <div id="matches">
                <RequestMatchesSection />
              </div>
            )}

            {activeTab === "Settings" && (
              <div id="settigns">
                <SettingsProfileSection user={user} />
              </div>
            )}
          </div>
        </div>
      </div>
      <PreFooterSpacer />
    </>
  );
}
