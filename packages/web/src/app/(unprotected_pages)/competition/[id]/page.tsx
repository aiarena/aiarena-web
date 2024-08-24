"use client";
import { useRouter } from "next/navigation";
import { useEffect, useState } from "react";
import Image from "next/image";
import competitionsData from "@/_data/mockCompetiton.json"; // Adjust path as necessary
import CompetitionHeader from "@/_components/_display/CompetitionHeader";
import ToggleDisplay from "@/_components/_display/ToggleDisplay";
import MapDisplay from "@/_components/_display/MapDisplay";
import VideoComponent from "@/_components/_display/VideoBanner";
import VideoPlayer from "@/_components/_display/VideoPlayer";


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

export default function Page() {
  const [competition, setCompetition] = useState<Competition | null>(null);
  const router = useRouter();
  const { id } = { id: "1" };

  useEffect(() => {
    
      const competitionData = mockCompetitions[1];
      setCompetition(competitionData);
    
  }, []);

  if (!competition) {
    return <div>Loading...</div>;
  }

  const renderRankings = (
    <div>
      {Object.entries(competition.rankings).map(
        ([division, participants], divisionIdx) => (
          <div key={divisionIdx} className="mb-6">
            <h3 className="text-2xl font-bold mb-4 text-customGreen">
              {division.replace(/division/, "Division ")}
            </h3>
            <table className="w-full text-left">
              <thead>
                <tr className="bg-gray-700">
                  <th className="px-4 py-2">Rank</th>
                  <th className="px-4 py-2">Name</th>
                  <th className="px-4 py-2">Race</th>
                  <th className="px-4 py-2">Author</th>
                  <th className="px-4 py-2">Type</th>
                  <th className="px-4 py-2">Win %</th>
                  <th className="px-4 py-2">ELO</th>
                  <th className="px-4 py-2">Trend</th>
                </tr>
              </thead>
              <tbody>
                {participants.map((participant: Participant, idx: number) => (
                  <tr
                    key={idx}
                    className="border-t border-gray-600 hover:bg-gray-700 transition cursor-pointer"
                  >
                    <td className="px-4 py-2">{participant.rank}</td>
                    <td className="px-4 py-2 font-semibold text-customGreen hover:text-white transition">
                      {participant.name}
                    </td>
                    <td className="px-4 py-2">{participant.race}</td>
                    <td className="px-4 py-2">{participant.author}</td>
                    <td className="px-4 py-2">{participant.type}</td>
                    <td className="px-4 py-2">{participant.winRate}%</td>
                    <td className="px-4 py-2">{participant.elo}</td>
                    <td className="px-4 py-2">{participant.trend}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )
      )}
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
              <td className="px-4 py-2">{round.roundNumber}</td>
              <td className="px-4 py-2">{round.startedAt}</td>
              <td className="px-4 py-2">
                {round.finishedAt ? round.finishedAt : "Ongoing"}
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
        imageUrl={competition.imageUrl}
        status={competition.opened}
      />

      {/* Main Content Section */}
      <div className="px-4 sm:px-6 lg:px-8 max-w-9xl mx-auto space-y-6">
        {/* Competition Details and About Section */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          {/* Basic Info */}
          <div className="bg-gray-900 p-6 rounded-lg shadow-md">
            <h3 className="text-2xl font-semibold text-customGreen mb-4">
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

            <h3 className="text-2xl font-semibold text-customGreen my-4">
              Maps
            </h3>
            <div className="flex flex-wrap justify-center gap-4">
              {competition.maps.map((mapName, index) => (
                <div
                  key={index}
                  className="flex-none w-28 h-28"
                >
                  <MapDisplay
                    mapName={mapName}
                    imageUrl={`/maps/oceanborn.jpg`} // Static image for demonstration
                  />
                </div>
              ))}
            </div>
          </div>

          {/* Live Stream Section */}
          <div className="bg-gray-800 p-6 rounded-lg shadow-md lg:col-span-2">
            <h2 className="text-3xl font-bold text-customGreen mb-4">
              Live Stream
            </h2>
            <div className="relative ">
              <VideoPlayer
                src="/ai-banner.mp4" // Local or hosted video file
                poster="/images/video-poster.jpg" // Optional poster image
                alt="Sample video demonstrating the AI competition."
                controls={true}
                autoPlay={true}
                loop={true}
                muted={true}
              />
            </div>
          </div>
        </div>

        {/* Toggle Display Section */}
        <ToggleDisplay rankings={renderRankings} rounds={renderRounds} />
      </div>
    </div>
  );
}
