"use client";
import { useUserContext } from "@/_components/providers/UserProvider";
import { useSignOut } from "@/_components/_hooks/useSignOut";
import { useRouter } from "next/navigation";
import { useEffect, useState } from "react";
import TabNavigation from "@/_components/_nav/TabNav";
import BotOverview from "@/_components/_display/BotOverview";
import PreFooterSpacer from "@/_components/_display/PreFooterSpacer";

export default function Page() {
  const [signOut] = useSignOut();
  const router = useRouter();
  const { user, setUser, fetching } = useUserContext();
  const [activeTab, setActiveTab] = useState("Bots");

  useEffect(() => {
    if (user === null && fetching === false) {
      router.push("/");
    }
  }, [user, fetching, router]);

  return (
    <>
      <div className="min-h-screen flex justify-center">
        <div className="mx-auto py-8 px-4 max-w-7xl bg-gray-800 w-full">
          {/* Navigation Tabs */}
          <TabNavigation
            tabs={[
              { name: "Bots", href: "#bot-overview" },
              { name: "Achievements", href: "#achievements" },
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
                <BotOverview />
              </div>
            )}

            {activeTab === "Achievements" && (
              <div id="achievements">
                <h2 className="text-2xl font-semibold text-white mb-4">
                  Achievements
                </h2>
                <p>Achievements Content</p>
              </div>
            )}

            {activeTab === "Requested Matches" && (
              <div id="matches">
                <h2 className="text-2xl font-semibold text-white mb-4">
                  Requested Matches
                </h2>
                <p>Requested Matches Content</p>
              </div>
            )}

            {activeTab === "Settings" && (
              <div id="settings">
                <h2 className="text-2xl font-semibold text-white mb-4">
                  Settings
                </h2>
                <p>Settings Content</p>
              </div>
            )}
          </div>
        </div>
      </div>
      <PreFooterSpacer />
    </>
  );
}
