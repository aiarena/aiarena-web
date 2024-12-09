"use client";
import { useState } from "react";
import Link from "next/link";
import FilterableList from "./FilterableList";
import { formatDate } from "@/_lib/dateUtils";

// Props inferred from Relay data
interface ClosedCompetitionListProps {
  competitions: {
    id: string;
    name: string;
    dateCreated: string;
    status: string;
  }[];
}

export default function ClosedCompetitionList({
  competitions,
}: ClosedCompetitionListProps) {
  return (
    <div>
      <FilterableList
        data={competitions}
        fields={["name", "dateCreated", "status"]} // Pass nested field as string
        fieldLabels={{
          name: "Competition Name",
          dateCreated: "Date Created",
          status: "Status",
        }}
        fieldClasses={{
          // "name": "Competition Name",
          dateCreated: "hidden sm:block",
          status: "hidden md:block",
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
            <div className="grid grid-cols-[repeat(auto-fit,_minmax(0,_1fr))] w-full">
              <span className="text-left font-semibold text-customGreen  truncate">
                {item.name}
              </span>
              <span className="hidden sm:block text-left text-gray-200  truncate">
                {formatDate(item.dateCreated)}
              </span>
              <span className="hidden md:block text-left text-gray-200  truncate">
                {item.status}
              </span>
            </div>
          </Link>
        )}
      />
    </div>
  );
}
