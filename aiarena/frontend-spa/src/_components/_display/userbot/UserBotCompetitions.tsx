import { Suspense, useState } from "react";

import { extractRelayID, getNodes } from "@/_lib/relayHelpers";
import { graphql, useFragment } from "react-relay";
import ActiveDot from "../ActiveDot";
import SquareButton from "@/_components/_props/SquareButton";
import JoinCompetitionModal from "@/_components/_sections/_modals/JoinCompetitionModal";
import SuspenseGetLoading from "@/_components/_props/SuspenseGetLoading";
import { UserBotCompetitions_bot$key } from "./__generated__/UserBotCompetitions_bot.graphql";
import { ExclamationTriangleIcon } from "@heroicons/react/24/outline";

interface UserBotCompetitionProps {
  bot: UserBotCompetitions_bot$key;
}

export default function UserBotCompetitions(props: UserBotCompetitionProps) {
  const bot = useFragment(
    graphql`
      fragment UserBotCompetitions_bot on BotType {
        id
        name
        competitionParticipations {
          edges {
            node {
              active
              id
              competition {
                id
                name
                status
              }
              elo
              divisionNum
              crashPerc
              crashCount
              trend
              matchCount
              winPerc
              lossPerc
            }
          }
        }
        ...JoinCompetitionModal_bot
      }
    `,
    props.bot
  );
  const comp_data = getNodes(bot.competitionParticipations);

  const [isJoinCompetitionModalOpen, setJoinCompetitionModalOpen] =
    useState(false);
  const [isJoinCompetitionModalLoading, setIsJoinCompetitionModalLoading] =
    useState(false);

  const activeCompetitions = (comp_data ?? []).filter((e) => e.active);
  const hasCompetitions = activeCompetitions.length > 0;

  return (
    <div className="p-2 bg-darken-4 rounded-b-lg ">
      {/* Competitions Header */}
      <div
        className={`${
          hasCompetitions ? " mb-2 border-b  border-gray-800 pb-2 " : ""
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
          isLoading={isJoinCompetitionModalLoading}
          textColor="dim"
        />
      </div>

      {/* List Active Competitions */}
      <div className="space-y-4 ">
        {activeCompetitions.map((participation) => (
          <div
            key={participation.id}
            className="border border-neutral-700 rounded-sm transition-all shadow-lg shadow-black p-4 grid grid-cols-1 md:grid-cols-2 gap-4 "
          >
            {/* Left Column: Competition Name & Stats */}
            <div className="space-y-2">
              <div className="flex items-center space-x-2 border-b border-gray-600 pb-2">
                <div>
                  <ActiveDot />
                </div>
                <a
                  href={`/competitions/${extractRelayID(participation.competition.id, "CompetitionType")}`}
                  className="text-sm font-semibold"
                >
                  {participation.competition.name}
                </a>
              </div>
              <div className="text-sm text-left flex flex-wrap ">
                <span className="font-bold text-gray-300 mr-4 block ">
                  Division:{" "}
                  <span className="font-normal">
                    {participation.divisionNum}
                  </span>
                </span>
                <span className="font-bold text-gray-300 mr-4 block">
                  Current ELO:{" "}
                  <span className="font-normal">{participation.elo}</span>
                </span>
                <span className="font-bold text-gray-300 mr-4 block">
                  Trend:{" "}
                  <span
                    className={`font-normal ${
                      (participation.trend ?? 0) > 0 ? "text-customGreen" : ""
                    }${
                      (participation.trend ?? 0) === 0 ? "text-gray-300" : ""
                    }${(participation.trend ?? 0) < 0 ? "text-red-500" : ""}`}
                  >
                    {participation.trend ?? 0}
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
                <span className="font-bold">Matches:</span>
                <span className="">{participation.matchCount}</span>
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
                  {(participation.winPerc ?? 0).toFixed(1)}%
                </span>
                <span>/</span>
                <span className="text-red-500 font-medium">
                  {(participation.lossPerc ?? 0).toFixed(1)}%
                </span>
              </div>
              <div className="flex items-center space-x-2 flex-wrap">
                <ExclamationTriangleIcon
                  aria-label="Danger icon"
                  className={`size-5 ${participation.crashCount > 0 ? "text-red-500" : "text-gray-300"}`}
                  role="img"
                />
                <span className="font-bold">Crashes:</span>
                <span
                  className={`${participation.crashCount > 0 ? "text-red-500" : "text-gray-300"} font-medium `}
                >
                  {participation.crashCount}
                </span>
              </div>
              <a
                href={`/competitions/stats/${extractRelayID(participation.id, "CompetitionParticipationType")}`}
              >
                Explore more stats
              </a>
            </div>
          </div>
        ))}
      </div>

      {/* Join Competition Modal */}

      {isJoinCompetitionModalOpen && (
        <Suspense
          fallback={
            <SuspenseGetLoading setLoading={setIsJoinCompetitionModalLoading} />
          }
        >
          <JoinCompetitionModal
            isOpen={isJoinCompetitionModalOpen}
            bot={bot}
            onClose={() => setJoinCompetitionModalOpen(false)}
          />
        </Suspense>
      )}
    </div>
  );
}
