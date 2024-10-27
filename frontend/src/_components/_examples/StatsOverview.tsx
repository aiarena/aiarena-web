import React from "react";

const StatsOverview: React.FC<{ stats: { label: string; value: string }[] }> = ({ stats }) => {
  return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-8">
      {stats.map((stat, index) => (
        <div key={index} className="bg-white rounded-lg shadow-md p-6 text-center hover:shadow-lg transition-shadow duration-300">
          <h4 className="text-3xl font-bold text-gray-800 mb-2">{stat.value}</h4>
          <p className="text-gray-600">{stat.label}</p>
        </div>
      ))}
    </div>
  );
};

export default StatsOverview;
