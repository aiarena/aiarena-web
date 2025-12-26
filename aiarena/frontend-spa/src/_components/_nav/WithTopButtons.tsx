import {
  statsSideNavbarLinks,
  statsTopNavbarLinks,
} from "@/_pages/Rework/CompetitionParticipation/StatsSideNavbarLinks";
import clsx from "clsx";
import { Dispatch, ReactNode, SetStateAction } from "react";

export default function WithTopButtons({
  children,
  activeTab,
  activeTopTab,
  setActiveTopTab,
}: {
  children: ReactNode;
  activeTab: (typeof statsSideNavbarLinks)[number]["state"];
  setActiveTab: Dispatch<
    SetStateAction<(typeof statsSideNavbarLinks)[number]["state"]>
  >;

  activeTopTab: (typeof statsTopNavbarLinks)[number]["state"];
  setActiveTopTab: Dispatch<
    SetStateAction<(typeof statsTopNavbarLinks)[number]["state"]>
  >;
}) {
  return (
    <div>
      <div className="w-full pb-2">
        {statsTopNavbarLinks
          .filter((it) => it.parent === activeTab)
          .map((tab) => (
            <button
              key={tab.name}
              onClick={() => setActiveTopTab(tab.state)}
              className={clsx(
                "m-1 px-4 py-2 text-white border-1 bg-darken-2 shadow-black shadow-sm  duration-300 ease-in-out transform backdrop-blur-sm text-center",
                tab.state === activeTopTab
                  ? "text-large border-neutral-700 border-b-customGreen border-b-2"
                  : "border-neutral-700 hover:border-b-customGreen border-b-2"
              )}
            >
              <p className="text-gray-100 text-l text-center">{tab.name}</p>
            </button>
          ))}
      </div>
      <main role="main">{children}</main>
    </div>
  );
}
