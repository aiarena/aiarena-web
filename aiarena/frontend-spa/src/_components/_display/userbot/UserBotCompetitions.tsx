import { Suspense, useState } from "react";
import { graphql, useFragment } from "react-relay";
import { getNodes } from "@/_lib/relayHelpers";
import SquareButton from "@/_components/_actions/SquareButton";
import JoinCompetitionModal from "@/_pages/UserBots/UserBotsSection/_modals/JoinCompetitionModal";
import SuspenseGetLoading from "@/_components/_actions/SuspenseGetLoading";
import { UserBotCompetitions_bot$key } from "./__generated__/UserBotCompetitions_bot.graphql";
import clsx from "clsx";
import UserBotParticipationCard from "./UserBotParticipationCard";

interface UserBotCompetitionProps {
  bot: UserBotCompetitions_bot$key;
}

export default function UserBotCompetitions(props: UserBotCompetitionProps) {
  const bot = useFragment(
    graphql`
      fragment UserBotCompetitions_bot on BotType {
        id
        name

        activeCompetitionParticipations: competitionParticipations(
          active: true
        ) {
          edges {
            node {
              id
              ...UserBotParticipationCard_participation
            }
          }
        }

        ...JoinCompetitionModal_bot
      }
    `,
    props.bot,
  );

  const activeCompetitions = getNodes(bot.activeCompetitionParticipations);

  const [isJoinCompetitionModalOpen, setJoinCompetitionModalOpen] =
    useState(false);
  const [isJoinCompetitionModalLoading, setIsJoinCompetitionModalLoading] =
    useState(false);

  const hasActiveCompetitions = activeCompetitions.length > 0;

  return (
    <div className="p-2 bg-darken-4 rounded-b-lg">
      {/* Competitions Header */}
      <div
        className={clsx(
          "flex justify-between flex-wrap w-full gap-4",
          hasActiveCompetitions && "mb-2 border-b border-gray-800 pb-2",
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

        <SquareButton
          text="Edit Participations"
          onClick={() => setJoinCompetitionModalOpen(true)}
          isLoading={isJoinCompetitionModalLoading}
          textColor="dim"
        />
      </div>

      {/* Competitions List */}
      <div className="space-y-4">
        {activeCompetitions.map((competitionParticipation) => (
          <UserBotParticipationCard
            key={competitionParticipation.id}
            participation={competitionParticipation}
          />
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
