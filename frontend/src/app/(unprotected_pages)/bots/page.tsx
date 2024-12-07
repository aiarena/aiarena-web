"use client";

import CompetitionCard from "@/_components/_display/CompetitionCard";
import ClosedCompetitionList from "@/_components/_display/CompetitionList";

import FilterableList from "@/_components/_display/FilterableList";
import WrappedTitle from "@/_components/_display/WrappedTitle";
import mockBots from "@/_data/mockBots.json";
import { formatDate } from "@/_lib/dateUtils";
import Link from "next/link";



export default function Page() {
  return (
    <>
  
  <FilterableList
  data={mockBots}
  fields={["name", "created", "type", "user.username"]} // Pass nested field as string
  fieldLabels={{
    "name": "Bot Name",
    "created": "Date Created",
    "user.username": "User", 
    "type": "Type",
  }}
  filters={[
    {
      type: "search",
      label: "Search",
      field: "all",
      placeholder: "Search all fields...",
    },
    {
      type: "dropdown",
      label: "Type",
      field: "type",
      placeholder: "Select type",
    },
  ]}
  renderRow={(item, index) => (
    <Link
      href={`/bot/${item.id}`}
      className="block p-4 hover:bg-gray-800 rounded transition flex justify-between items-center shadow-md border border-gray-700"
    >
         <div className="grid grid-cols-[repeat(4,_minmax(0,_1fr))] gap-4 w-full">
      <span className="text-left font-semibold text-customGreen">{item.name}</span>
      <span className="text-left text-gray-200">{formatDate(item.created)}</span>
      <span className="text-left text-gray-200">{item.type}</span>
      <span className="text-left text-gray-200">{item.user.username}</span>
    </div>
{/* 

      <span className="text-left w-1/4 font-semibold text-customGreen">
        {item.name}
      </span>
      <span className="text-left w-1/4 text-gray-200">{formatDate(item.created)}</span>
      <span className="text-left w-1/4 text-gray-200">{item.type}</span>
      <span className="text-left w-1/4 text-gray-200">
        {item.user.username}
      </span> */}
    </Link>
  )}
/>
</>   
  );
}
