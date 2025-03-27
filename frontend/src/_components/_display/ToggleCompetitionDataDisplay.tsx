import React, { useState } from "react";
import { useCompetitionData } from "../_hooks/useCompetitionData";

import Link from "next/link";
import { getPublicPrefix } from "@/_lib/getPublicPrefix";
import Image from "next/image";
import LoadingDots from "./LoadingDots";

interface ToggleCompetitionDataDisplayProps {
  competitionId: string;
}

// Mapping for Patreon icons
const patreonIcons: Record<string, string> = {
  BRONZE: "bronze.png",
  SILVER: "silver.png",
  GOLD: "gold.png",
  PLATINUM: "platinum.png",
  DIAMOND: "diamond.png",
};

export default function ToggleCompetitionDataDisplay(
  props: ToggleCompetitionDataDisplayProps
) {
  const [activeTab, setActiveTab] = useState<"rankings" | "rounds">("rankings");

  const competitionData = useCompetitionData(props.competitionId);

  if (!competitionData) {
    return (
      <div className="pt-12 pb-24 items-center">
        <p>Loading rounds and competition rankings...</p>
        <LoadingDots className={"pt-2"} />
      </div>
    );
  }

  if (!competitionData.participants || !competitionData.rounds) {
    return <div>Error loading competition data</div>;
  }

  const handleTabClick = (tab: "rankings" | "rounds") => {
    setActiveTab(tab);
  };

  const renderRankings = (
    <div>
      {(() => {
        // Group participants by divisionNum
        const divisions = competitionData.participants.reduce(
          (acc, participant) => {
            const division = participant.divisionNum;
            if (!acc[division]) {
              acc[division] = [];
            }
            acc[division].push(participant);
            return acc;
          },
          {} as Record<number, typeof competitionData.participants>
        );

        // Render each division
        return Object.entries(divisions).map(([divisionNum, participants]) => (
          <div key={divisionNum} className="mb-6">
            <h3 className="text-2xl font-bold mb-4 text-customGreen">
              Division {divisionNum}
            </h3>
            <div className="overflow-hidden">
              <table className="w-full table-fixed text-left">
                <thead>
                  <tr className="bg-gray-700">
                    <th className="px-4 py-2 truncate">Rank</th>
                    <th className="px-4 py-2 truncate">Name</th>
                    <th className="px-4 py-2 truncate">Author</th>
                    <th className="px-4 py-2 truncate">Type</th>
                    <th className="px-4 py-2 truncate">ELO</th>
                    <th className="px-4 py-2 truncate">Trend</th>
                    <th className="px-4 py-2 truncate">Patreon Level</th>
                  </tr>
                </thead>
                <tbody>
                  {participants.map((participant, idx) => {
                    const patreonLevel =
                      participant.bot?.user?.patreonLevel || "NONE";
                    const iconSrc = patreonIcons[patreonLevel];

                    return (
                      <tr
                        key={participant.id}
                        className="border-t border-gray-600 hover:bg-gray-700 transition"
                      >
                        <td className="px-4 py-2 truncate">{idx + 1}</td>
                        <td className="px-4 py-2 font-semibold  transition truncate">
                          <Link
                            href={`${getPublicPrefix()}/bots/${participant.bot?.id}`}
                            className=" cursor-pointer text-customGreen hover:text-white"
                          >
                            {participant.bot?.name || "Unknown"}
                          </Link>
                        </td>
                        <td className="px-4 py-2 font-semibold  transition truncate">
                          <Link
                            href={`${getPublicPrefix()}/authors/${participant.bot?.user?.id}`}
                            className=" cursor-pointer text-customGreen hover:text-white"
                          >
                            {participant.bot?.user?.username || "Unknown"}
                          </Link>
                        </td>
                        <td className="px-4 py-2 truncate">
                          {participant.bot?.type || "N/A"}
                        </td>
                        <td className="px-4 py-2 truncate">
                          {participant.elo}
                        </td>
                        <td
                          className={`px-4 py-2 truncate ${
                            participant?.trend && participant?.trend > 0
                              ? "text-green-500"
                              : ""
                          } ${
                            participant?.trend && participant?.trend < 0
                              ? "text-red-500"
                              : ""
                          }`}
                        >
                          {participant.trend}
                        </td>
                        <td className="px-4 py-2 truncate">
                          {iconSrc ? (
                            <Image
                              src={`/bot-icons/${iconSrc}`}
                              width={20}
                              height={20}
                              alt={`${patreonLevel} Patreon Level`}
                            />
                          ) : null}
                        </td>
                      </tr>
                    );
                  })}
                </tbody>
              </table>
            </div>
          </div>
        ));
      })()}
    </div>
  );

  const renderRounds = (
    <div>
      <table className="w-full text-left">
        <thead>
          <tr className="bg-gray-700">
            <th className="px-4 py-2">Round #</th>
            <th className="px-4 py-2">Started At</th>
            <th className="px-4 py-2">Finished At</th>
          </tr>
        </thead>
        <tbody>
          {competitionData.rounds.map((round, idx) => (
            <tr
              key={idx}
              className="border-t border-gray-600 hover:bg-gray-700 transition"
            >
              <td className="px-4 py-2">{round.number}</td>
              <td className="px-4 py-2">
                {new Date(round.started).toLocaleString()}
              </td>
              <td className="px-4 py-2">
                {round.finished
                  ? new Date(round.finished).toLocaleString()
                  : "Ongoing"}
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );

  return (
    <div>
      <div className="mt-8">
        <div className="flex justify-center space-x-4 mb-6">
          <button
            className={`px-4 py-2 font-semibold rounded-lg transition ${
              activeTab === "rankings"
                ? "bg-customGreen text-white"
                : "bg-gray-700 text-gray-300 hover:bg-gray-600"
            }`}
            onClick={() => handleTabClick("rankings")}
          >
            Rankings
          </button>
          <button
            className={`px-4 py-2 font-semibold rounded-lg transition ${
              activeTab === "rounds"
                ? "bg-customGreen text-white"
                : "bg-gray-700 text-gray-300 hover:bg-gray-600"
            }`}
            onClick={() => handleTabClick("rounds")}
          >
            Rounds
          </button>
        </div>

        <div>
          {activeTab === "rankings" && renderRankings}
          {activeTab === "rounds" && renderRounds}
        </div>
      </div>
    </div>
  );
}
