import React, { useState } from "react";
import MainButton from "@/_components/_props/MainButton";
import SquareButton from "@/_components/_props/SquareButton";

import JoinCompetitionModal from "./JoinCompetitionModal";

import { ProfileBotProps } from "@/_components/_display/ProfileBot";

export default function BotCompetitionsSection({ bot }: ProfileBotProps) {
  const [isJoinCompetitionModalOpen, setJoinCompetitionModalOpen] =
    useState(false);

  const activeCompetitions = (bot?.competitionParticipations ?? []).filter(
    (e) => e.active
  );
  const hasCompetitions = activeCompetitions.length > 0;

  return (
    <div className="p-2">
      {/* Competitions Header */}
      <div
        className={`${
          hasCompetitions ? " mb-2 border-b border-gray-600 pb-2 " : ""
        } flex justify-between flex-wrap w-full gap-4`}
      >
        {hasCompetitions ? (
          <h4 className="text-left pt-2 text-sm font-semibold text-gray-300">
            {`${activeCompetitions.length}`} Active{" "}
            {activeCompetitions.length === 1 ? "Competition" : "Competitions"}
          </h4>
        ) : (
          <p className="ml-2 text-left pt-2 text-sm font-semibold text-gray-400">
            Your bot is not currently participating in any competitions,
            consider joining a competition.
          </p>
        )}
        <SquareButton
          text="Edit Competitions"
          onClick={() => setJoinCompetitionModalOpen(true)}
        />
      </div>

      {/* List Active Competitions */}
      <div className="space-y-4">
        {activeCompetitions.map((comp, index) => (
          <div
            key={index}
            className="cursor-pointer border border-gray-600 rounded-lg bg-gray-700 hover:bg-gray-700 hover:border-gray-500 transition-all shadow-md shadow-black p-4 grid grid-cols-1 md:grid-cols-2 gap-4"
          >
            {/* Left Column: Competition Name & Stats */}
            <div className="space-y-2">
              <div className="flex items-center space-x-2 border-b border-gray-600 pb-2">
                <div>
                  <div className="circular-gradient-shadow"></div>
                </div>
                <p className="ml-16 text-sm font-semibold text-customGreen">
                  {comp.competition.name}
                </p>
              </div>
              <div className="text-sm text-left flex flex-wrap ">
                <span className="font-bold text-gray-300 mr-4 block ">
                  Division:{" "}
                  <span className="font-normal">{comp.divisionNum}</span>
                </span>
                <span className="font-bold text-gray-300 mr-4 block">
                  Current ELO: <span className="font-normal">{comp.elo}</span>
                </span>
                <span className="font-bold text-gray-300 mr-4 block">
                  Trend:{" "}
                  <span
                    className={`font-normal ${
                      (comp.trend ?? 0) > 0 ? "text-customGreen" : ""
                    }${(comp.trend ?? 0) === 0 ? "text-gray-300" : ""}${
                      (comp.trend ?? 0) < 0 ? "text-red-500" : ""
                    }`}
                  >
                    {comp.trend ?? 0}
                  </span>
                </span>
              </div>
            </div>

            {/* Right Column: Match Data */}
            <div className="space-y-2 text-sm text-gray-300">
              <div className="flex items-center space-x-2 flex-wrap">
                <svg
                  xmlns="http://www.w3.org/2000/svg"
                  className="h-5 w-5 text-gray-300"
                  fill="none"
                  viewBox="0 0 24 24"
                  stroke="currentColor"
                  strokeWidth={2}
                >
                  <circle
                    cx="12"
                    cy="12"
                    r="9"
                    stroke="currentColor"
                    strokeWidth="2"
                  />
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    d="M10 8l6 4-6 4V8z"
                  />
                </svg>
                <span className="font-bold ">Matches:</span>
                <span className="">{comp.matchCount}</span>
                <span className="pl-4 font-bold">Crashes:</span>
                <span className="text-red-500 font-medium">
                  {comp.crashCount}
                </span>
              </div>
              <div className="flex items-center space-x-2 flex-wrap">
                <svg
                  xmlns="http://www.w3.org/2000/svg"
                  className="h-5 w-5 text-gray-300"
                  fill="none"
                  viewBox="0 0 24 24"
                  stroke="currentColor"
                  strokeWidth={2}
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    d="M4 4v6h6M20 20v-6h-6M7.778 16.222a8.002 8.002 0 0011.446 0m.007-8.444a8.002 8.002 0 00-11.46 0"
                  />
                </svg>
                <span className="font-bold">Win/Loss:</span>
                <span className="text-customGreen font-medium">
                  {(comp.winPerc ?? 0).toFixed(1)}%
                </span>
                <span>/</span>
                <span className="text-red-500 font-medium">
                  {(comp.lossPerc ?? 0).toFixed(1)}%
                </span>
              </div>
              <div className="flex items-center space-x-2 flex-wrap">
                <svg
                  xmlns="http://www.w3.org/2000/svg"
                  className="h-5 w-5 text-red-500"
                  fill="none"
                  viewBox="0 0 24 24"
                  stroke="currentColor"
                  strokeWidth={2}
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    d="M12 8v4m0 4h.01M2.93 4.49l8.61 15.01a1 1 0 001.74 0l8.61-15.01a1 1 0 00-.87-1.5H3.8a1 1 0 00-.87 1.5z"
                  />
                </svg>
                <span className="font-bold">Crashes:</span>
                <span className="text-red-500 font-medium">
                  {" "}
                  {(comp.crashPerc ?? 0).toFixed(1)}%
                </span>
              </div>
              <div></div>
            </div>
          </div>
        ))}
      </div>

      {/* Join Competition Modal */}

      {isJoinCompetitionModalOpen && (
        <JoinCompetitionModal
          isOpen={isJoinCompetitionModalOpen}
          bot={bot}
          onClose={() => setJoinCompetitionModalOpen(false)}
        />
      )}
    </div>
  );
}
