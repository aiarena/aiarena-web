"use client";
import { useRouter } from "next/navigation";
import { useEffect, useState } from "react";
import Image from "next/image";
import competitionsData from "@/_data/mockCompetiton.json";
import CompetitionHeader from "@/_components/_display/CompetitionHeader";
import ToggleDisplay from "@/_components/_display/ToggleDisplay";
import MapDisplay from "@/_components/_display/MapDisplay";
import VideoComponent from "@/_components/_display/VideoBanner";
import VideoPlayer from "@/_components/_display/VideoPlayer";
import { getFeatureFlags } from "@/_data/featureFlags";
import { useCompetition } from "@/_components/_hooks/useCompetition";
import { getPublicPrefix } from "@/_lib/getPublicPrefix";

// Types
interface Participant {
  rank: number;
  name: string;
  race: string;
  author: string;
  type: string;
  winRate: string;
  elo: number;
  trend: string;
}

interface Round {
  roundNumber: number;
  startedAt: string;
  finishedAt: string | null;
}

interface Competition {
  name: string;
  created: string;
  opened: string;
  status: string;
  progress: number;
  topPlayers: string[];
  participants: number;
  totalGames: number;
  imageUrl: string;
  maps: string[];
  rankings: {
    division1: Participant[];
    division2: Participant[];
    division3: Participant[];
    division4: Participant[];
    // Add more divisions if needed
  };
  rounds: Round[];
}

interface CompetitionsData {
  [key: string]: Competition;
}

const mockCompetitions: CompetitionsData = competitionsData;

interface CompetitionPageProps {
  params: {
    id: string;
  };
}

// Mapping for Patreon icons
const patreonIcons: Record<string, string> = {
  BRONZE: "bronze.png",
  SILVER: "silver.png",
  GOLD: "gold.png",
  PLATINUM: "platinum.png",
  DIAMOND: "diamond.png",
  // Add other levels as needed
};

export default function Page({ params }: CompetitionPageProps) {
  // const [competition, setCompetition] = useState<Competition | null>(null);
  const competition = useCompetition(params.id); // Fetch competitions from the hook
  console.log(competition);
  console.log(params);
  const router = useRouter();
  const { id } = { id: "1" };

  const featureFlags = getFeatureFlags();

  // useEffect(() => {
  //   const competitionData = mockCompetitions[1];
  //   setCompetition(competitionData);
  // }, []);

  if (!competition) {
    // This block is removed to let errors propagate
    throw new Error("Competition data is missing.");
  }
  const renderRankings = (
    <div>
      {(() => {
        // Group participants by divisionNum
        const divisions = competition.participants.reduce(
          (acc, participant) => {
            const division = participant.divisionNum;
            if (!acc[division]) {
              acc[division] = [];
            }
            acc[division].push(participant);
            return acc;
          },
          {} as Record<number, typeof competition.participants>
        );

        // Render each division
        return Object.entries(divisions).map(([divisionNum, participants]) => (
          <div key={divisionNum} className="mb-6">
            <h3 className="text-2xl font-bold mb-4 text-customGreen">
              Division {divisionNum}
            </h3>
            <div className="overflow-hidden">
              <table className="w-full table-fixed text-left">
                <thead>
                  <tr className="bg-gray-700">
                    <th className="px-4 py-2 truncate">Rank</th>
                    <th className="px-4 py-2 truncate">Name</th>
                    <th className="px-4 py-2 truncate">Author</th>
                    <th className="px-4 py-2 truncate">Type</th>
                    <th className="px-4 py-2 truncate">ELO</th>
                    <th className="px-4 py-2 truncate">Trend</th>
                    <th className="px-4 py-2 truncate">Patreon Level</th>
                  </tr>
                </thead>
                <tbody>
                  {participants.map((participant, idx) => {
                    const patreonLevel =
                      participant.bot?.user?.patreonLevel || "NONE";
                    const iconSrc = patreonIcons[patreonLevel];

                    return (
                      <tr
                        key={participant.id}
                        className="border-t border-gray-600 hover:bg-gray-700 transition cursor-pointer"
                      >
                        <td className="px-4 py-2 truncate">{idx + 1}</td>
                        <td className="px-4 py-2 font-semibold text-customGreen hover:text-white transition truncate">
                          {participant.bot?.name || "Unknown"}
                        </td>
                        <td className="px-4 py-2 font-semibold transition truncate">
                          {participant.bot?.user?.username || "Unknown"}
                        </td>
                        <td className="px-4 py-2 truncate">
                          {participant.bot?.type || "N/A"}
                        </td>
                        <td className="px-4 py-2 truncate">
                          {participant.elo}
                        </td>
                        <td
                          className={`px-4 py-2 truncate ${
                            participant?.trend && participant?.trend > 0
                              ? "text-green-500"
                              : ""
                          } ${
                            participant?.trend && participant?.trend < 0
                              ? "text-red-500"
                              : ""
                          }`}
                        >
                          {participant.trend}
                        </td>
                        <td className="px-4 py-2 truncate">
                          {iconSrc ? (
                            <Image
                              src={`/bot-icons/${iconSrc}`}
                              width={20}
                              height={20}
                              alt={`${patreonLevel} Patreon Level`}
                            />
                          ) : null}
                        </td>
                      </tr>
                    );
                  })}
                </tbody>
              </table>
            </div>
          </div>
        ));
      })()}
    </div>
  );

  const renderRounds = (
    <div>
      <table className="w-full text-left">
        <thead>
          <tr className="bg-gray-700">
            <th className="px-4 py-2">Round #</th>
            <th className="px-4 py-2">Started At</th>
            <th className="px-4 py-2">Finished At</th>
          </tr>
        </thead>
        <tbody>
          {competition.rounds.map((round, idx) => (
            <tr
              key={idx}
              className="border-t border-gray-600 hover:bg-gray-700 transition"
            >
              <td className="px-4 py-2">{round.number}</td>
              <td className="px-4 py-2">
                {new Date(round.started).toLocaleString()}
              </td>
              <td className="px-4 py-2">
                {round.finished
                  ? new Date(round.finished).toLocaleString()
                  : "Ongoing"}
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );

  return (
    <div className="space-y-6">
      {/* Header Section */}
      <CompetitionHeader
        name={competition.name}
        imageUrl={"/competitions/sc2_1.webp"}
        status={competition.status}
      />

      {/* Main Content Section */}
      <div className=" px-4 sm:px-6 lg:px-8 max-w-9xl mx-auto space-y-6">
        {/* Competition Details and About Section */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          {/* Basic Info */}
          <div className="border-gray-800 border-2 bg-customBackgroundColor1D1 p-6 rounded-lg shadow-md">
            <h3 className=" text-2xl font-semibold text-customGreen mb-4">
              Competition Details
            </h3>
            <div className="space-y-2 text-white">
              {/* You can add more details here if needed */}
            </div>

            <p className="text-white leading-relaxed">
              The SC2 AI Arena 2024 Season 2 competition is the ultimate proving
              ground for bots, featuring the main SC2 AI ladder with all
              official maps and standard melee rules. It rigorously tests
              strategy, micro, resource management, and decision-making.
            </p>
            {/* {featureFlags.competitionMaps ? (
              <div className="pt-4">
                <h3 className="text-2xl font-semibold text-customGreen my-4">
                  Maps
                </h3>
                <div className="flex flex-wrap justify-center gap-4">
                  {competition.maps.map((mapName, index) => (
                    <div key={index} className="flex-none w-28 h-28">
                      <MapDisplay
                        mapName={mapName}
                        imageUrl={`/maps/oceanborn.jpg`} // Static image for demonstration
                      />
                    </div>
                  ))}
                </div>
              </div>
            ) : null} */}
          </div>
          {featureFlags.competitionMaps && !featureFlags.competitionVideo ? (
            <div className="border-gray-700 border-2 bg-customBackgroundColor1  rounded-lg shadow-md lg:col-span-2">
              <h3 className=" text-2xl font-semibold text-customGreen my-4">
                Maps
              </h3>
              <div className="flex flex-wrap justify-center gap-4">
                {competition.maps.map((map, index) => (
                  <div key={map.id} className="flex-none w-28 h-28">
                    <MapDisplay
                      mapName={map.name}
                      imageUrl={`/${map.file}.webp`} // Assuming images are named based on file paths
                      
                    />
                  </div>
                ))}
              </div>
            </div>
          ) : null}

          {featureFlags.competitionVideo ? (
            <div className="border-gray-700 border-2 bg-customBackgroundColor1  p-6 rounded-lg shadow-md lg:col-span-2">
              <h2 className="text-3xl font-bold text-customGreen mb-4">
                Live Stream
              </h2>
              <div className="relative ">
                <VideoPlayer
                  src="/videos/ai-banner.mp4" // Local or hosted video file
                  poster="/images/video-poster.jpg" // Optional poster image
                  alt="Sample video demonstrating the AI competition."
                  controls={true}
                  autoPlay={true}
                  loop={true}
                  muted={true}
                />
              </div>
            </div>
          ) : null}
        </div>

        {/* Toggle Display Section */}
        <ToggleDisplay rankings={renderRankings} rounds={renderRounds} />
      </div>
    </div>
  );
}
