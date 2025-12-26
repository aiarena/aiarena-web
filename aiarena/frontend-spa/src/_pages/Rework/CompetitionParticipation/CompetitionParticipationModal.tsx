import Modal from "@/_components/_actions/Modal";
import { Suspense, useState } from "react";
import {
  statsSideNavbarLinks,
  statsTopNavbarLinks,
} from "./StatsSideNavbarLinks";
import WithStatsSideButtons from "@/_components/_nav/WithStatsSideButtons";
import WithTopButtons from "@/_components/_nav/WithTopButtons";
import LoadingSpinner from "@/_components/_display/LoadingSpinnerGray";
import CompetitionParticipationStats from "./CompetitionParticipationStats";
import { getIDFromBase64 } from "@/_lib/relayHelpers";
import { StatsModalStatus } from "../Bot/Page";
import NoItemsInListMessage from "@/_components/_display/NoItemsInListMessage";

interface CompetitionParticipationModalProps {
  isOpen: boolean;
  onClose: () => void;
  modalStatus: StatsModalStatus;
}

export default function CompetitionParticipationModal({
  isOpen,
  onClose,
  modalStatus,
}: CompetitionParticipationModalProps) {
  const [activeTab, setActiveTab] =
    useState<(typeof statsSideNavbarLinks)[number]["state"]>("overview");

  const [activeTopTab, setActiveTopTab] =
    useState<(typeof statsTopNavbarLinks)[number]["state"]>("elograph");
  const id = getIDFromBase64(modalStatus.botId, "CompetitionParticipationType");
  if (!id) {
    return <NoItemsInListMessage>Unable to decode Id</NoItemsInListMessage>;
  }
  return (
    <>
      <Modal
        onClose={onClose}
        isOpen={isOpen}
        title={`${modalStatus.botName} - ${modalStatus.competitionName} stats`}
        size="l"
        padding={2}
        paddingX={2}
      >
        <section
          aria-labelledby="competition-participation-heading"
          className="min-h-[90vh]"
        >
          <h2 id="competition-participation-heading" className="sr-only">
            Competition Participation Stats
          </h2>

          <WithStatsSideButtons
            activeTab={activeTab}
            setActiveTab={setActiveTab}
            setActiveTopTab={setActiveTopTab}
          >
            <WithTopButtons
              activeTab={activeTab}
              setActiveTab={setActiveTab}
              activeTopTab={activeTopTab}
              setActiveTopTab={setActiveTopTab}
            >
              <Suspense fallback={<LoadingSpinner color="light-gray" />}>
                <CompetitionParticipationStats
                  id={id}
                  activeTab={activeTab}
                  setActiveTab={setActiveTab}
                  activeTopTab={activeTopTab}
                  setActiveTopTab={setActiveTopTab}
                />
              </Suspense>
            </WithTopButtons>
          </WithStatsSideButtons>
        </section>
      </Modal>
    </>
  );
}
