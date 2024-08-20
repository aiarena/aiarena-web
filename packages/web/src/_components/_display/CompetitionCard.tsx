import Image from "next/image";
import Link from "next/link";

interface CompetitionCardProps {
  competition: {
    name: string;
    created: string;
    opened: string;
    status: string;
    progress: number;
    topPlayers: string[];
    participants: number;
    totalGames: number;
    imageUrl: string;
  };
}
export default function CompetitionCard({ competition }: CompetitionCardProps) {
  return (
    <Link
      href={`/competition/${competition.name}`} // Assuming each competition has a unique ID or URL
      className="block bg-gray-900 text-white shadow-lg rounded-lg overflow-hidden hover:bg-gray-800 transition transform hover:scale-105"
    >
      <div className="flex">
        <div className="w-1/3">
          <Image
            width={1920}
            height={1080}
            src={competition.imageUrl}
            alt={competition.name}
            className="object-cover h-full"
          />
        </div>
        <div className="w-2/3 p-6">
          <h3 className="text-2xl font-bold mb-2">{competition.name}</h3>
          <p className="mb-1">Created: {competition.created}</p>
          <p className="mb-1">Opened: {competition.opened}</p>
          <p className="mb-4">Status: {competition.status}</p>
          <div className="flex items-center mb-2">
            <p className="mr-2">Top 3 Players:</p>
            {competition.topPlayers.map((player, index) => (
              <span
                key={index}
                className="mr-2 cursor-pointer text-customGreen hover:text-white hover:underline transition"
                // onClick={() => console.log("hi")}
              >
                {player}
              </span>
            ))}
          </div>
          <p className="mb-1">Participants: {competition.participants}</p>
          <p>Total Games Played: {competition.totalGames}</p>
          <div className="mt-4">
            <p className="mb-2">Competition Progress</p>
            <div className="relative pt-1">
              <div className="overflow-hidden h-2 text-xs flex rounded bg-gray-700">
                <div
                  style={{ width: `${competition.progress}%` }}
                  className="shadow-none flex flex-col text-center whitespace-nowrap text-white justify-center bg-customGreen"
                ></div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </Link>
  );
}