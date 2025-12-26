import { Suspense, useState } from "react";
import Bot from "./Bot";
import LoadingSpinner from "@/_components/_display/LoadingSpinnerGray";
import CompetitionParticipationModal from "../CompetitionParticipation/CompetitionParticipationModal";

export type StatsModalStatus = {
  status: boolean;
  botId: string | undefined;
  competitionName: string | undefined;
  botName: string | undefined;
};

export default function BotPage() {
  const [isStatsModalOpen, setIsStatsModalOpen] = useState<StatsModalStatus>({
    status: false,
    botId: undefined,
    competitionName: undefined,
    botName: undefined,
  });

  return (
    <>
      <Suspense fallback={<LoadingSpinner color="light-gray" />}>
        <Bot
          isStatsModalOpen={isStatsModalOpen}
          setIsStatsModalOpen={setIsStatsModalOpen}
        />
      </Suspense>
      {isStatsModalOpen.status && (
        <Suspense fallback={<LoadingSpinner color="light-gray" />}>
          <CompetitionParticipationModal
            isOpen={isStatsModalOpen.status}
            onClose={() =>
              setIsStatsModalOpen({
                status: false,
                botId: undefined,
                competitionName: undefined,
                botName: undefined,
              })
            }
            modalStatus={isStatsModalOpen}
          />
        </Suspense>
      )}
    </>
  );
}
