"use client";

import CompetitionCard from "@/_components/_display/CompetitionCard";
import ClosedCompetitionList from "@/_components/_display/CompetitionList";

import FilterableList from "@/_components/_display/FilterableList";
import TitleWrapper from "@/_components/_display/TitleWrapper";
import mockBots from "@/_data/mockBots.json";
import { formatDate } from "@/_lib/dateUtils";
import Link from "next/link";
import {getFeatureFlags} from "@/_data/featureFlags"
import { notFound } from "next/navigation"; 


export default function Page() {
  const botsPage = getFeatureFlags().botsPage
  if (!botsPage) {
    notFound();
    return null; 
  }

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

  fieldClasses={{
    "user.username": "hidden md:block", 
    "type": "hidden sm:block",
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
      <div className="grid grid-cols-[repeat(auto-fit,_minmax(0,_1fr))]  w-full">
      <span  className="text-left font-semibold text-customGreen  truncate">{item.name}</span>
      <span className="text-left text-gray-200  truncate">{formatDate(item.created)}</span>
      <span  className="hidden md:block text-left text-gray-200  truncate">{item.type}</span>
      <span  className=" hidden sm:block text-left text-gray-200  truncate">{item.user.username}</span>
    </div>
    </Link>
  )}
/>
</>   
  );
}
