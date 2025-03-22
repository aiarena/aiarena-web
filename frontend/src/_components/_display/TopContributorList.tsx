import React from "react";

interface Contributor {
  name: string;
  amount: number;
}

interface TopContributorsListProps {
  contributors: Contributor[];
}

const TopContributorsList: React.FC<TopContributorsListProps> = ({
  contributors,
}) => {
  return (
    <div className="overflow-x-auto w-full">
      <div className="flex items-center justify-center relative">
        <div className="flex-1 h-[2px] bg-gradient-to-l from-customGreen to-transparent"></div>

        <h3 className="text-lg font-bold mb-2 text-center px-4">
          Top contributors
        </h3>
        <div className="flex-1 h-[2px] bg-gradient-to-r from-customGreen to-transparent"></div>
      </div>
      <table className="min-w-full table-auto">
        <thead>
          <tr>
            <th className="px-4 py-2">Name</th>
            <th className="px-4 py-2">Amount</th>
          </tr>
        </thead>
        <tbody>
          {contributors.map((contributor, index) => (
            <tr key={index}>
              <td className="border px-4 py-2">{contributor.name}</td>
              <td className="border px-4 py-2">
                ${contributor.amount.toFixed(2)}
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
};

export default TopContributorsList;
