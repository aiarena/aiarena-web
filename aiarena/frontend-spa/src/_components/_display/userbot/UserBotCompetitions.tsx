import { Suspense, useState } from "react";
import { getIDFromBase64, getNodes } from "@/_lib/relayHelpers";
import { graphql, useFragment } from "react-relay";
import ActiveDot from "../ActiveDot";
import SquareButton from "@/_components/_actions/SquareButton";
import JoinCompetitionModal from "@/_pages/UserBots/UserBotsSection/_modals/JoinCompetitionModal";
import SuspenseGetLoading from "@/_components/_actions/SuspenseGetLoading";
import { UserBotCompetitions_bot$key } from "./__generated__/UserBotCompetitions_bot.graphql";
import { ExclamationTriangleIcon } from "@heroicons/react/24/outline";
import SimpleToggle from "@/_components/_actions/_toggle/SimpleToggle";
import { getDotColor } from "@/_lib/getDotColor";
import clsx from "clsx";
import { Link } from "react-router";

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

  const compData = getNodes(bot.competitionParticipations);
  const [displayAllCompetitions, setDisplayAllCompetitions] = useState(false);
  const [isJoinCompetitionModalOpen, setJoinCompetitionModalOpen] =
    useState(false);
  const [isJoinCompetitionModalLoading, setIsJoinCompetitionModalLoading] =
    useState(false);

  const activeCompetitions = (compData ?? []).filter((e) => e.active);
  const displayCompetitions = displayAllCompetitions
    ? compData
    : activeCompetitions;

  const hasActiveCompetitions = activeCompetitions.length > 0;
  const hasInactiveCompetitions =
    compData.length - activeCompetitions.length > 0;

  return (
    <div className="p-2 bg-darken-4 rounded-b-lg">
      {/* Competitions Header */}
      <div
        className={clsx(
          "flex justify-between flex-wrap w-full gap-4",
          hasActiveCompetitions && "mb-2 border-b border-gray-800 pb-2"
        )}
      >
        {hasActiveCompetitions ? (
          <h4 className="text-left pt-2 text-sm font-semibold text-gray-300">
            {`${activeCompetitions.length}`} Active{" "}
            {activeCompetitions.length === 1 ? "Competition" : "Competitions"}
          </h4>
        ) : (
          <p className="ml-2 text-left pt-2 text-sm font-semibold text-gray-400">
            Your bot is not currently participating in any active competitions,
            consider joining a competition.
          </p>
        )}
        <div className="flex flex-wrap gap-4">
          {hasInactiveCompetitions && (
            <label className="flex items-center gap-2 cursor-pointer">
              <SimpleToggle
                enabled={displayAllCompetitions}
                onChange={() =>
                  setDisplayAllCompetitions(!displayAllCompetitions)
                }
              />
              <span>Show All</span>
            </label>
          )}
          <SquareButton
            text="Edit Participations"
            onClick={() => setJoinCompetitionModalOpen(true)}
            isLoading={isJoinCompetitionModalLoading}
            textColor="dim"
          />
        </div>
      </div>

      {/* List Active Competitions */}
      <div className="space-y-4">
        {displayCompetitions.map((competitionParticipation) => {
          const dotColor = getDotColor(
            competitionParticipation.active,
            competitionParticipation.competition.status ?? ""
          );

          return (
            <div
              key={competitionParticipation.id}
              className="border border-neutral-700 rounded-sm transition-all shadow-lg shadow-black p-4 grid grid-cols-1 md:grid-cols-2 gap-4"
            >
              {/* Left Column */}
              <div className="space-y-2">
                <div className="flex items-center space-x-2 border-b border-gray-600 pb-2">
                  <div
                    title={`Competition Status: ${competitionParticipation.competition.status} \nParticipating: ${
                      competitionParticipation.active ? "Yes" : "No"
                    }`}
                  >
                    <ActiveDot color={dotColor} />
                  </div>
                  <Link
                    to={`/competitions/${getIDFromBase64(
                      competitionParticipation.competition.id,
                      "CompetitionType"
                    )}`}
                    className="text-sm font-semibold"
                  >
                    {competitionParticipation.competition.name}
                  </Link>
                </div>
                <div className="text-sm text-left flex flex-wrap">
                  <span className="font-bold text-gray-300 mr-4 block">
                    Division:{" "}
                    <span className="font-normal">
                      {competitionParticipation.divisionNum == 0
                        ? "Placements"
                        : competitionParticipation.divisionNum}
                    </span>
                  </span>
                  <span className="font-bold text-gray-300 mr-4 block">
                    Current ELO:{" "}
                    <span className="font-normal">
                      {competitionParticipation.elo}
                    </span>
                  </span>
                </div>
              </div>

              {/* Right Column */}
              <div className="space-y-2 text-sm text-gray-300">
                {/* Match Count */}
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
                  <span>{competitionParticipation.matchCount}</span>
                </div>

                {/* Win/Loss */}
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
                    {(competitionParticipation.winPerc ?? 0).toFixed(1)}%
                  </span>
                  <span>/</span>
                  <span className="text-red-500 font-medium">
                    {(competitionParticipation.lossPerc ?? 0).toFixed(1)}%
                  </span>
                </div>

                {/* Crashes */}
                <div className="flex items-center space-x-2 flex-wrap">
                  <ExclamationTriangleIcon
                    aria-label="Danger icon"
                    role="img"
                    className={clsx(
                      "size-5",
                      competitionParticipation.crashCount > 0
                        ? "text-red-500"
                        : "text-gray-300"
                    )}
                  />
                  <span className="font-bold">Crashes:</span>
                  <span
                    className={clsx(
                      "font-medium",
                      competitionParticipation.crashCount > 0
                        ? "text-red-500"
                        : "text-gray-300"
                    )}
                  >
                    {competitionParticipation.crashCount}
                  </span>
                </div>

                <a
                  href={`/competitions/stats/${getIDFromBase64(
                    competitionParticipation.id,
                    "CompetitionParticipationType"
                  )}`}
                >
                  Explore more stats
                </a>
              </div>
            </div>
          );
        })}
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
