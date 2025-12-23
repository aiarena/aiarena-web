import { Suspense, useState } from "react";
import CompetitionParticipationModal from "./CompetitionParticipationModal";
import LoadingSpinner from "@/_components/_display/LoadingSpinnerGray";

export default function StatsButton({ id }: { id: string }) {
  const [isBiographyModalOpen, setBiographyModalOpen] = useState<{
    state: boolean;
    id: string | null;
  }>({ state: false, id: null });
  return (
    <>
      <div className="flex gap-2 items-center">
        <button
          className="text-customGreen"
          onClick={() => setBiographyModalOpen({ state: true, id: id })}
        >
          Stats
        </button>
        <Suspense fallback={<LoadingSpinner color="white" />}>
          {isBiographyModalOpen.state && isBiographyModalOpen.id != null && (
            <CompetitionParticipationModal
              isOpen={isBiographyModalOpen.state}
              onClose={() => setBiographyModalOpen({ state: false, id: null })}
              id={isBiographyModalOpen.id}
            />
          )}
        </Suspense>
      </div>
    </>
  );
}
