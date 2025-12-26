import { Suspense, useState } from "react";
import CompetitionParticipationModal from "./CompetitionParticipationModal";
import LoadingSpinner from "@/_components/_display/LoadingSpinnerGray";
import { StatsModalStatus } from "../Bot/Page";

export default function StatsButton({
  StatsModalStatus,
}: {
  StatsModalStatus: StatsModalStatus;
}) {
  const [isBiographyModalOpen, setBiographyModalOpen] = useState<{
    state: boolean;
    id: string | undefined;
  }>({ state: false, id: undefined });
  return (
    <>
      <div className="flex gap-2 items-center">
        <button
          className="text-customGreen"
          onClick={() =>
            setBiographyModalOpen({ state: true, id: StatsModalStatus.botId })
          }
        >
          Stats
        </button>
        <Suspense fallback={<LoadingSpinner color="white" />}>
          {isBiographyModalOpen.state && isBiographyModalOpen.id != null && (
            <CompetitionParticipationModal
              isOpen={isBiographyModalOpen.state}
              onClose={() =>
                setBiographyModalOpen({ state: false, id: undefined })
              }
              modalStatus={StatsModalStatus}
            />
          )}
        </Suspense>
      </div>
    </>
  );
}
