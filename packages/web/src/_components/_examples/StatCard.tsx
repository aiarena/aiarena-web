import React from "react";

const StatCard: React.FC<{ stat: string; description: string }> = ({ stat, description }) => {
  return (
    <div className="bg-gradient-to-r from-purple-500 to-indigo-500 text-white rounded-lg shadow-md p-6 text-center hover:shadow-lg transition-shadow duration-300">
      <h2 className="text-4xl font-bold mb-2">{stat}</h2>
      <p className="text-lg">{description}</p>
    </div>
  );
};

export default StatCard;
