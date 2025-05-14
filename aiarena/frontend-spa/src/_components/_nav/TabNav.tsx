import React from "react";

interface Tab {
  name: string;
  href: string;
}

interface TabNavigationProps {
  tabs: Tab[];
  activeTab: string;
  setActiveTab: (tabName: string) => void;
}

const TabNavigation: React.FC<TabNavigationProps> = ({
  tabs,
  activeTab,
  setActiveTab,
}) => {
  return (
    <div className="border-b border-slate-500">
      <div className="flex flex-wrap justify-center md:justify-start space-x-4 md:space-x-6">
        {tabs.map((tab) => (
          <a
            key={tab.name}
            href={tab.href}
            onClick={(e) => {
              e.preventDefault();
              setActiveTab(tab.name);
            }}
            className={`px-3 py-2 text-sm md:text-base font-semibold ${
              activeTab === tab.name
                ? "text-customGreen border-b-2 border-customGreen"
                : "text-gray-200 hover:text-white"
            }`}
          >
            {tab.name}
          </a>
        ))}
      </div>
    </div>
  );
};

export default TabNavigation;
