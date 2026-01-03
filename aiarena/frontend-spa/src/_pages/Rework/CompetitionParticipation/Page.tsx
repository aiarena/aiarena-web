import { Suspense, useState } from "react";
import { useParams } from "react-router";
import LoadingSpinner from "@/_components/_display/LoadingSpinnerGray";
import CompetitionParticipationStats from "./CompetitionParticipationStats";
import {
  statsSideNavbarLinks,
  statsTopNavbarLinks,
} from "./StatsSideNavbarLinks";
import WithStatsSideButtons from "@/_components/_nav/WithStatsSideButtons";
import WithTopButtons from "@/_components/_nav/WithTopButtons";
import NameCompDisplay from "./NameCompDisplay";

export default function Page() {
  const { id } = useParams<{ id: string }>();
  const [activeTab, setActiveTab] =
    useState<(typeof statsSideNavbarLinks)[number]["state"]>("overview");

  const [activeTopTab, setActiveTopTab] =
    useState<(typeof statsTopNavbarLinks)[number]["state"]>("elograph");

  if (!id) {
    return (
      <div className="text-center py-12">
        <p className="text-gray-400">Invalid competition participation ID</p>
      </div>
    );
  }

  return (
    <section aria-labelledby="competition-participation-heading">
      <h2 id="competition-participation-heading" className="sr-only">
        Competition Participation Stats
      </h2>

      <Suspense fallback={<LoadingSpinner color="light-gray" />}>
        <NameCompDisplay id={id} />
      </Suspense>
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
  );
}
