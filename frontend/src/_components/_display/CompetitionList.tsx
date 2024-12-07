"use client"
import { useState } from "react";
import Link from "next/link";
import FilterableList from "./FilterableList";
import { formatDate } from "@/_lib/dateUtils";

interface ClosedCompetition {
  name: string;
  dateCreated: string;
  opened: string;
  status: string;
}

interface ClosedCompetitionListProps {
  competitions: ClosedCompetition[];
}

export default function ClosedCompetitionList({
  competitions,
}: ClosedCompetitionListProps) {
  // const [sortField, setSortField] = useState<keyof ClosedCompetition>("status");
  // const [sortOrder, setSortOrder] = useState<"asc" | "desc">("desc");

  // const sortedCompetitions = [...competitions].sort((a, b) => {
  //   if (sortOrder === "asc") {
  //     return a[sortField] > b[sortField] ? 1 : -1;
  //   } else {
  //     return a[sortField] < b[sortField] ? 1 : -1;
  //   }
  // });

  // const handleSort = (field: keyof ClosedCompetition) => {
  //   if (field === sortField) {
  //     setSortOrder(sortOrder === "asc" ? "desc" : "asc");
  //   } else {
  //     setSortField(field);
  //     setSortOrder("asc");
  //   }
  // };

  return (
    <div>
        <FilterableList
  data={competitions}
  fields={["name", "dateCreated", "status", ]} // Pass nested field as string
  fieldLabels={{
    "name": "Competition Name",
    "dateCreated": "Date Created",
    "status": "Status", 
  }}
  fieldClasses={{
    // "name": "Competition Name",
    "dateCreated": "hidden sm:block", 
    "status": "hidden md:block", 
  }}
  
  filters={[
    {
      type: "search",
      label: "Search",
      field: "all",
      placeholder: "Search all fields...",
    },
  ]}
  resultsPerPage={5}
  
  renderRow={(item, index) => (
    <Link
      href={`/competition/${item.id}`}
      className="block p-4 hover:bg-gray-800 rounded transition flex justify-between items-center shadow-md border border-gray-700"
    >
      <div className="grid grid-cols-[repeat(auto-fit,_minmax(0,_1fr))]  gap-4 w-full">
      <span className="text-left font-semibold text-customGreen">{item.name}</span>
      <span className="hidden sm:block text-left text-gray-200">{formatDate(item.dateCreated)}</span>
      <span className="hidden md:block text-left text-gray-200">{item.status}</span>
    </div>
    
    </Link>
  )}
/>
      {/* <div className="grid grid-cols-3 gap-4 text-white mb-4">
        <button
          className="text-left font-bold text-customGreen hover:text-white"
          onClick={() => handleSort("name")}
        >
          Name
        </button>
        <button
          className="text-left font-bold text-customGreen hover:text-white"
          onClick={() => handleSort("dateCreated")}
        >
          Created
        </button>
       
        <button
          className="text-left font-bold text-customGreen hover:text-white"
          onClick={() => handleSort("status")}
        >
          Status
        </button>
      </div>
      <ul className="text-white">
        {sortedCompetitions.map((comp, index) => (
          <li key={index} className="mb-2">
            <Link
              href={`/competition/${index}`}
              className="block p-2 hover:bg-gray-700 rounded transition flex justify-between items-center"
            >
              <span className="text-left w-1/4">{comp.name}</span>
              <span className="text-left w-1/4">{comp.dateCreated}</span>
            
              <span className="text-left w-1/4">{comp.status}</span>
            </Link>
          </li>
        ))}
      </ul> */}

      {/* Pagination Buttons */}
      {/* <div className="flex justify-center items-center mt-6 space-x-2">
        <button className="px-3 py-1 rounded bg-gray-700 hover:bg-gray-600 text-white">{"<"}</button>
        <button className="px-3 py-1 rounded bg-gray-700 hover:bg-gray-600 text-white">1</button>
        <button className="px-3 py-1 rounded bg-gray-700 hover:bg-gray-600 text-white">2</button>
        <button className="px-3 py-1 rounded bg-gray-700 hover:bg-gray-600 text-white">3</button>
        <button className="px-3 py-1 rounded bg-gray-700 hover:bg-gray-600 text-white">4</button>
        <button className="px-3 py-1 rounded bg-gray-700 hover:bg-gray-600 text-white">5</button>
        <button className="px-3 py-1 rounded bg-gray-700 hover:bg-gray-600 text-white">6</button>
        <button className="px-3 py-1 rounded bg-gray-700 hover:bg-gray-600 text-white">78</button>
        <button className="px-3 py-1 rounded bg-gray-700 hover:bg-gray-600 text-white">{">"}</button>
      </div> */}
    </div>
  );
}