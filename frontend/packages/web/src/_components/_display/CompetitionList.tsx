"use client"
import { useState } from "react";
import Link from "next/link";

interface ClosedCompetition {
  name: string;
  created: string;
  opened: string;
  closed: string;
}

interface ClosedCompetitionListProps {
  competitions: ClosedCompetition[];
}

export default function ClosedCompetitionList({
  competitions,
}: ClosedCompetitionListProps) {
  const [sortField, setSortField] = useState<keyof ClosedCompetition>("closed");
  const [sortOrder, setSortOrder] = useState<"asc" | "desc">("desc");

  const sortedCompetitions = [...competitions].sort((a, b) => {
    if (sortOrder === "asc") {
      return a[sortField] > b[sortField] ? 1 : -1;
    } else {
      return a[sortField] < b[sortField] ? 1 : -1;
    }
  });

  const handleSort = (field: keyof ClosedCompetition) => {
    if (field === sortField) {
      setSortOrder(sortOrder === "asc" ? "desc" : "asc");
    } else {
      setSortField(field);
      setSortOrder("asc");
    }
  };

  return (
    <div>
      <div className="grid grid-cols-4 gap-4 text-white mb-4">
        <button
          className="text-left font-bold text-customGreen hover:text-white"
          onClick={() => handleSort("name")}
        >
          Name
        </button>
        <button
          className="text-left font-bold text-customGreen hover:text-white"
          onClick={() => handleSort("created")}
        >
          Created
        </button>
        <button
          className="text-left font-bold text-customGreen hover:text-white"
          onClick={() => handleSort("opened")}
        >
          Opened
        </button>
        <button
          className="text-left font-bold text-customGreen hover:text-white"
          onClick={() => handleSort("closed")}
        >
          Closed
        </button>
      </div>
      <ul className="text-white">
        {sortedCompetitions.map((comp, index) => (
          <li key={index} className="mb-2">
            <Link
              href={`/competition/${index}`} // Assuming each competition has a unique ID or URL
              className="block p-2 hover:bg-gray-700 rounded transition flex justify-between items-center"
            >
              <span className="text-left w-1/4">{comp.name}</span>
              <span className="text-left w-1/4">{comp.created}</span>
              <span className="text-left w-1/4">{comp.opened}</span>
              <span className="text-left w-1/4">{comp.closed}</span>
            </Link>
          </li>
        ))}
      </ul>

      {/* Pagination Buttons */}
      <div className="flex justify-center items-center mt-6 space-x-2">
        <button className="px-3 py-1 rounded bg-gray-700 hover:bg-gray-600 text-white">{"<"}</button>
        <button className="px-3 py-1 rounded bg-gray-700 hover:bg-gray-600 text-white">1</button>
        <button className="px-3 py-1 rounded bg-gray-700 hover:bg-gray-600 text-white">2</button>
        <button className="px-3 py-1 rounded bg-gray-700 hover:bg-gray-600 text-white">3</button>
        <button className="px-3 py-1 rounded bg-gray-700 hover:bg-gray-600 text-white">4</button>
        <button className="px-3 py-1 rounded bg-gray-700 hover:bg-gray-600 text-white">5</button>
        <button className="px-3 py-1 rounded bg-gray-700 hover:bg-gray-600 text-white">6</button>
        <button className="px-3 py-1 rounded bg-gray-700 hover:bg-gray-600 text-white">78</button>
        <button className="px-3 py-1 rounded bg-gray-700 hover:bg-gray-600 text-white">{">"}</button>
      </div>
    </div>
  );
}