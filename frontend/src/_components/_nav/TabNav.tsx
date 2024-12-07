import React, { useState } from 'react';

interface Tab {
  name: string;
  href: string;
  active?: boolean;
}

interface TabNavigationProps {
  tabs: Tab[];
}

const TabNavigation: React.FC<TabNavigationProps> = ({ tabs }) => {
  const [activeTab, setActiveTab] = useState<string>(tabs[0].name);

  return (
    <div className="flex space-x-4 border-b border-slate-500">
      {tabs.map((tab) => (
        <a
          key={tab.name}
          href={tab.href}
          onClick={() => setActiveTab(tab.name)}
          className={`px-4 py-2 font-semibold ${
            activeTab === tab.name
              ? 'text-customGreen border-b-2 border-customGreen'
              : 'text-gray-200 hover:text-white'
          }`}
        >
          {tab.name}
        </a>
      ))}
      
    </div>
  );
};

export default TabNavigation;
