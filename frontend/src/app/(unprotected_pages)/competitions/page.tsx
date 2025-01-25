"use client"
import CompetitionCard from "@/_components/_display/CompetitionCard";
import ClosedCompetitionList from "@/_components/_display/CompetitionList";
import PreFooterSpacer from "@/_components/_display/PreFooterSpacer";
import TitleWrapper from "@/_components/_display/TitleWrapper";
// import { useCompetition } from "@/_components/_hooks/useCompetition";
import { useCompetitions } from "@/_components/_hooks/useCompetitions";
import { getPublicPrefix } from "@/_lib/getPublicPrefix";
import { useEffect, useState } from "react";


// const mockData = {
//   activeCompetitions: [
//     {
//       name: "Sc2 AI Arena 2024 Season 2",
//       created: "11. June 2024 - 06:47:31",
//       opened: "11. June 2024 - 20:52:33",
//       status: "Open",
//       progress: 75, // example progress value
//       topPlayers: ["Player1", "Player2", "Player3"],
//       participants: 150,
//       totalGames: 1200,
//       imageUrl: `/competitions/sc2_1.webp`, // Placeholder image URL
//     },
//     {
//       name: "Sc2 AI Arena Micro Ladder",
//       created: "09. Aug. 2023 - 08:41:29",
//       opened: "15. Aug. 2023 - 15:47:20",
//       status: "Open",
//       progress: 50, // example progress value
//       topPlayers: ["PlayerA", "PlayerB", "PlayerC"],
//       participants: 100,
//       totalGames: 900,
//       imageUrl: `/competitions/sc2.webp`, // Placeholder image URL
//     },
//   ],
//   closedCompetitions: [
//     {
//       name: "Sc2 AI Arena 2024 Pre-Season 2",
//       created: "16. March 2024 - 13:20:26",
//       opened: "17. March 2024 - 01:11:31",
//       closed: "11. June 2024 - 07:23:50",
//     },
//     {
//       name: "Sc2 AI Arena 2024 Season 1",
//       created: "15. Feb. 2024 - 21:39:09",
//       opened: "16. Feb. 2024 - 09:54:04",
//       closed: "12. March 2024 - 13:37:03",
//     },
//     {
//       name: "Sc2 AI Arena 2024 Pre-Season 2",
//       created: "16. March 2024 - 13:20:26",
//       opened: "17. March 2024 - 01:11:31",
//       closed: "11. June 2024 - 07:23:50",
//     },
//     {
//       name: "Sc2 AI Arena 2024 Season 1",
//       created: "15. Feb. 2024 - 21:39:09",
//       opened: "16. Feb. 2024 - 09:54:04",
//       closed: "12. March 2024 - 13:37:03",
//     },
//     {
//       name: "Sc2 AI Arena 2024 Pre-Season 2",
//       created: "16. March 2024 - 13:20:26",
//       opened: "17. March 2024 - 01:11:31",
//       closed: "11. June 2024 - 07:23:50",
//     },
//     {
//       name: "Sc2 AI Arena 2024 Season 1",
//       created: "15. Feb. 2024 - 21:39:09",
//       opened: "16. Feb. 2024 - 09:54:04",
//       closed: "12. March 2024 - 13:37:03",
//     },
//     // Add more closed competitions here...
//   ],
// };

export default function Page() {
  const compData = useCompetitions(); // Fetch competitions from the hook

  console.log(compData)

  // Filter active and closed competitions directly
  const validCompetitions = (compData || []).filter((comp) => comp !== null && comp !== undefined);
  const activeCompetitions = validCompetitions.filter((comp) => comp.status === "OPEN");
  const closedCompetitions = validCompetitions.filter((comp) => comp.status === "CLOSED");

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
      <h1 className="text-4xl font-bold mb-10 text-customGreen font-gugi">The Arena</h1>

      {/* Active Competitions */}
      <section className="mb-16">
        <TitleWrapper title="Open Competitions" />
        <div className="space-y-8 mt-8">
          {activeCompetitions.length > 0 ? (
            activeCompetitions.map((comp, index) => (
              <CompetitionCard key={index} competition={comp} imageUrl={getBackgroundImage(comp.name)}/>
            ))
          ) : (
            <p>Competitions are loading...</p>
          )}
        </div>
      </section>

      {/* Closed Competitions */}
      <section>
        <TitleWrapper title="Closed Competitions" />
        {closedCompetitions.length > 0 ? (
          <ClosedCompetitionList competitions={closedCompetitions} />
        ) : (
          <p>Closed competitions are loading...</p>
        )}
      </section>
    </div>
    <PreFooterSpacer/>
    </>
  );
}