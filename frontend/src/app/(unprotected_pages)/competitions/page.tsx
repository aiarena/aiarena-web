"use client";
import CompetitionCard from "@/_components/_display/CompetitionCard";
import ClosedCompetitionList from "@/_components/_display/CompetitionList";
import PreFooterSpacer from "@/_components/_display/PreFooterSpacer";
import WrappedTitle from "@/_components/_display/WrappedTitle";
import { useCompetitions } from "@/_components/_hooks/useCompetitions";

export default function Page() {
  const compData = useCompetitions(); // Fetch competitions from the hook

  // Filter active and closed competitions directly
  const validCompetitions = (compData || []).filter(
    (comp) => comp !== null && comp !== undefined
  );
  const activeCompetitions = validCompetitions.filter(
    (comp) => comp.status === "OPEN"
  );
  const closedCompetitions = validCompetitions.filter(
    (comp) => comp.status === "CLOSED"
  );

  // Function to determine the background image
  const getBackgroundImage = (name: string) => {
    if (name.includes("Micro")) {
      return `/competitions/sc2.webp`;
    }
    if (/20\d{2}/.test(name)) {
      return `/competitions/sc2_1.webp`;
    }
    return `/competitions/sc2_1.webp`;
  };

  return (
    <>
      <div className="max-w-7xl mx-auto p-6">
        <h1 className="text-4xl font-bold mb-10 text-customGreen font-gugi">
          The Arena
        </h1>

        {/* Active Competitions */}
        <section className="mb-16">
          <WrappedTitle title="Open Competitions" />
          <div className="space-y-8 mt-8">
            {activeCompetitions.length > 0 ? (
              activeCompetitions.map((comp) => (
                <CompetitionCard
                  key={comp.id}
                  competition={comp}
                  imageUrl={getBackgroundImage(comp.name)}
                />
              ))
            ) : (
              <p>Competitions are loading...</p>
            )}
          </div>
        </section>

        {/* Closed Competitions */}
        <section>
          <WrappedTitle title="Closed Competitions" />
          {closedCompetitions.length > 0 ? (
            <ClosedCompetitionList competitions={closedCompetitions} />
          ) : (
            <p>Closed competitions are loading...</p>
          )}
        </section>
      </div>
      <PreFooterSpacer />
    </>
  );
}
